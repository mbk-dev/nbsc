"""Unit tests for the transport layer (endpoint fallback, error taxonomy) — no network."""

import warnings

import pytest

from nbsc import request_data
from nbsc.request_data import (
    NbsApiError,
    NbsEndpointError,
    NbsWafError,
    fetch_series,
)


VALID_PAYLOAD = {
    "state": 20000,
    "data": [
        {"code": "202501MM", "values": [{"value": "100.7"}]},
        {"code": "202502MM", "values": [{"value": "99.8"}]},
    ],
}


class FakeResponse:
    def __init__(self, status_code=200, payload=None, content_type="application/json"):
        self.status_code = status_code
        self._payload = payload
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise request_data.requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._payload


class FakeSession:
    """Returns queued responses in order; records every POSTed URL."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.posted_urls = []

    def post(self, url, json=None, timeout=None):
        self.posted_urls.append(url)
        return self._responses.pop(0)


def _install(monkeypatch, session):
    monkeypatch.setattr(request_data, "_make_session", lambda: session)


def _fetch():
    return fetch_series(cid="c1", indicator_id="i1", dts="202501MM-202512MM")


class TestEndpointFallback:
    def test_success_on_primary_endpoint(self, monkeypatch):
        session = FakeSession([FakeResponse(payload=VALID_PAYLOAD)])
        _install(monkeypatch, session)

        s = _fetch()

        assert len(session.posted_urls) == 1
        assert session.posted_urls[0].endswith("/stream/esData")
        assert len(s) == 2
        assert s.iloc[0] == pytest.approx(100.7)

    def test_fallback_to_legacy_endpoint_on_404(self, monkeypatch):
        session = FakeSession([FakeResponse(status_code=404), FakeResponse(payload=VALID_PAYLOAD)])
        _install(monkeypatch, session)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            s = _fetch()

        assert len(session.posted_urls) == 2
        assert session.posted_urls[1].endswith("/getEsDataByCidAndDt")
        assert len(s) == 2
        assert any("fallback" in str(w.message).lower() for w in caught)

    def test_all_endpoints_exhausted_raises(self, monkeypatch):
        session = FakeSession([FakeResponse(status_code=404), FakeResponse(status_code=405)])
        _install(monkeypatch, session)

        with pytest.raises(NbsEndpointError) as excinfo:
            _fetch()

        message = str(excinfo.value)
        assert "stream/esData" in message
        assert "getEsDataByCidAndDt" in message
        assert "NBSC_DATA_URL" in message

    def test_env_override_uses_only_that_url(self, monkeypatch):
        monkeypatch.setenv("NBSC_DATA_URL", "https://example.org/custom/esData")
        session = FakeSession([FakeResponse(payload=VALID_PAYLOAD)])
        _install(monkeypatch, session)

        s = _fetch()

        assert session.posted_urls == ["https://example.org/custom/esData"]
        assert len(s) == 2

    def test_env_override_failure_does_not_fall_back(self, monkeypatch):
        monkeypatch.setenv("NBSC_DATA_URL", "https://example.org/custom/esData")
        session = FakeSession([FakeResponse(status_code=404)])
        _install(monkeypatch, session)

        with pytest.raises(NbsEndpointError):
            _fetch()

        assert session.posted_urls == ["https://example.org/custom/esData"]


class TestErrorTaxonomy:
    def test_waf_challenge_raises_waf_error(self, monkeypatch):
        session = FakeSession([FakeResponse(payload=None, content_type="text/html;charset=utf-8")])
        _install(monkeypatch, session)

        with pytest.raises(NbsWafError):
            _fetch()

    def test_api_state_error(self, monkeypatch):
        session = FakeSession([FakeResponse(payload={"state": 10000, "message": "boom"})])
        _install(monkeypatch, session)

        with pytest.raises(NbsApiError, match="state=10000"):
            _fetch()

    def test_empty_data_warns_and_returns_empty_series(self, monkeypatch):
        session = FakeSession([FakeResponse(payload={"state": 20000, "data": []})])
        _install(monkeypatch, session)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            s = _fetch()

        assert s.empty
        assert any("codes.json" in str(w.message) for w in caught)
