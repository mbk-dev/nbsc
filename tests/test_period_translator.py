"""Unit tests for _dts_from_legacy and _parse_year_range — no network required."""

import warnings

import pytest

from nbsc.request_data import _dts_from_legacy, _parse_year_range


class TestDtsFromLegacy:
    def test_single_year_monthly(self):
        assert _dts_from_legacy("2026", "month") == "202601MM-202612MM"

    def test_single_year_annual(self):
        assert _dts_from_legacy("2026", "year") == "2026A-2026A"

    def test_range_monthly(self):
        assert _dts_from_legacy("2016-2020", "month") == "201601MM-202012MM"

    def test_range_annual(self):
        assert _dts_from_legacy("2016-2020", "year") == "2016A-2020A"

    def test_latest_monthly(self):
        result = _dts_from_legacy("LATEST10", "month")
        assert result.endswith("MM")
        parts = result.split("-")
        assert len(parts) == 2
        assert parts[0].endswith("MM")
        assert parts[1].endswith("MM")

    def test_last_annual(self):
        result = _dts_from_legacy("LAST5", "year")
        assert result.endswith("A")
        parts = result.split("-")
        assert len(parts) == 2

    def test_comma_list_monthly_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = _dts_from_legacy("2003,2012", "month")
            assert len(w) == 1
            assert "Comma-separated" in str(w[0].message)
        assert result == "200301MM-201212MM"

    def test_comma_list_annual(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = _dts_from_legacy("2003,2012", "year")
        assert result == "2003A-2012A"

    def test_whitespace_stripped(self):
        assert _dts_from_legacy("  2020  ", "month") == "202001MM-202012MM"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported period format"):
            _dts_from_legacy("abc", "month")

    def test_range_with_spaces(self):
        assert _dts_from_legacy("2016 - 2020", "month") == "201601MM-202012MM"


class TestParseYearRange:
    def test_single_year(self):
        assert _parse_year_range("2026") == (2026, 2026)

    def test_range(self):
        assert _parse_year_range("2016-2020") == (2016, 2020)

    def test_comma_list(self):
        assert _parse_year_range("2003,2012") == (2003, 2012)

    def test_latest(self):
        start, end = _parse_year_range("LATEST10")
        assert end - start == 9

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Cannot parse year range"):
            _parse_year_range("xyz")
