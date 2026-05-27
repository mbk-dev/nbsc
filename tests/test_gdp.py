"""Integration tests for GDP module — require network access to NBS.

Run with: NBSC_INTEGRATION=1 pytest tests/test_gdp.py -v
"""

import os

import pandas as pd
import pytest

from nbsc import gdp

pytestmark = pytest.mark.skipif(
    os.environ.get("NBSC_INTEGRATION") != "1",
    reason="Set NBSC_INTEGRATION=1 to run integration tests",
)


class TestGdpNominal:
    def test_returns_series_with_quarterly_index(self):
        s = gdp.get_gdp_nominal()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "Q-DEC"

    def test_recent_data_exists(self):
        s = gdp.get_gdp_nominal(first_year="2024")
        assert len(s) >= 4

    def test_values_are_positive_billions(self):
        s = gdp.get_gdp_nominal(first_year="2024")
        assert all(v > 10_000 for v in s.values)


class TestGdpReal:
    def test_returns_series_with_quarterly_index(self):
        s = gdp.get_gdp_real()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "Q-DEC"

    def test_recent_data_exists(self):
        s = gdp.get_gdp_real(first_year="2024")
        assert len(s) >= 4


class TestGdpIndex:
    def test_returns_series_with_quarterly_index(self):
        s = gdp.get_gdp_index()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "Q-DEC"

    def test_values_are_around_100(self):
        s = gdp.get_gdp_index(first_year="2024")
        assert all(90 < v < 130 for v in s.values)


class TestGdpQoqGrowth:
    def test_returns_series_with_quarterly_index(self):
        s = gdp.get_gdp_qoq_growth()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "Q-DEC"

    def test_values_are_percentage(self):
        s = gdp.get_gdp_qoq_growth(first_year="2024")
        assert all(-10 < v < 30 for v in s.values)
