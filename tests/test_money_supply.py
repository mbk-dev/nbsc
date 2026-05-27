"""Integration tests for money supply module — require network access to NBS.

Run with: NBSC_INTEGRATION=1 pytest tests/test_money_supply.py -v
"""

import os

import pandas as pd
import pytest

from nbsc import money_supply

pytestmark = pytest.mark.skipif(
    os.environ.get("NBSC_INTEGRATION") != "1",
    reason="Set NBSC_INTEGRATION=1 to run integration tests",
)


class TestM2:
    def test_returns_monthly_series(self):
        s = money_supply.get_m2()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_values_are_large(self):
        s = money_supply.get_m2(first_year="2024")
        assert len(s) >= 6
        assert all(v > 2_000_000 for v in s.values)


class TestM2Growth:
    def test_returns_monthly_series(self):
        s = money_supply.get_m2_yoy()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_values_are_percentage(self):
        s = money_supply.get_m2_yoy(first_year="2024")
        assert all(-5 < v < 30 for v in s.values)


class TestM1:
    def test_returns_monthly_series(self):
        s = money_supply.get_m1()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"


class TestM0:
    def test_returns_monthly_series(self):
        s = money_supply.get_m0()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"
