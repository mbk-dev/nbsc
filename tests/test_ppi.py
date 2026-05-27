"""Integration tests for PPI module — require network access to NBS.

Run with: NBSC_INTEGRATION=1 pytest tests/test_ppi.py -v
"""

import os

import pandas as pd
import pytest

from nbsc import ppi

pytestmark = pytest.mark.skipif(
    os.environ.get("NBSC_INTEGRATION") != "1",
    reason="Set NBSC_INTEGRATION=1 to run integration tests",
)


class TestPpiFactoryYoy:
    def test_returns_monthly_series(self):
        s = ppi.get_ppi_yoy()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_recent_data_exists(self):
        s = ppi.get_ppi_yoy(first_year="2024")
        assert len(s) >= 6

    def test_values_are_index(self):
        s = ppi.get_ppi_yoy(first_year="2024")
        assert all(80 < v < 130 for v in s.values)


class TestPpiFactoryMom:
    def test_returns_monthly_series(self):
        s = ppi.get_ppi_mom()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_values_are_index(self):
        s = ppi.get_ppi_mom(first_year="2024")
        assert all(90 < v < 110 for v in s.values)
