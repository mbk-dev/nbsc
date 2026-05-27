"""Integration tests for unemployment module — require network access to NBS.

Run with: NBSC_INTEGRATION=1 pytest tests/test_unemployment.py -v
"""

import os

import pandas as pd
import pytest

from nbsc import unemployment

pytestmark = pytest.mark.skipif(
    os.environ.get("NBSC_INTEGRATION") != "1",
    reason="Set NBSC_INTEGRATION=1 to run integration tests",
)


class TestUnemploymentRate:
    def test_returns_monthly_series(self):
        s = unemployment.get_unemployment_rate()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_recent_data_exists(self):
        s = unemployment.get_unemployment_rate(first_year="2024")
        assert len(s) >= 6

    def test_values_are_percentage(self):
        s = unemployment.get_unemployment_rate(first_year="2024")
        assert all(3.0 < v < 10.0 for v in s.values)
