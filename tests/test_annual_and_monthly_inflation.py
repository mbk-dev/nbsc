"""Integration tests for inflation module — require network access to NBS.

Run with: NBSC_INTEGRATION=1 pytest tests/test_annual_and_monthly_inflation.py
"""

import os

import pytest
from pytest import approx

from nbsc import inflation as infl

pytestmark = pytest.mark.skipif(
    os.environ.get("NBSC_INTEGRATION") != "1",
    reason="Set NBSC_INTEGRATION=1 to run integration tests",
)


def test_recent_inflation_has_values():
    s = infl.get_recent_inflation("2026")
    assert len(s) >= 1
    assert s.index.freqstr == "M"
    assert all(-0.1 < v < 0.1 for v in s.values)


def test_annual_inflation_2026_yoy():
    s = infl.get_annual_inflation("2026")
    assert len(s) >= 1
    assert s.index.freqstr == "M"
    last = s.iloc[0]
    assert 0.0 <= last <= 0.05


def test_annual_inflation_spans_multi_leaf():
    s = infl.get_annual_inflation("2021")
    assert len(s) >= 48
