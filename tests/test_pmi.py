"""Integration tests for PMI module — require network access to NBS.

Run with: NBSC_INTEGRATION=1 pytest tests/test_pmi.py -v
"""

import os

import pandas as pd
import pytest

from nbsc import pmi

pytestmark = pytest.mark.skipif(
    os.environ.get("NBSC_INTEGRATION") != "1",
    reason="Set NBSC_INTEGRATION=1 to run integration tests",
)


class TestManufacturingPmi:
    def test_returns_monthly_series(self):
        s = pmi.get_manufacturing_pmi()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_recent_data_exists(self):
        s = pmi.get_manufacturing_pmi(first_year="2024")
        assert len(s) >= 12

    def test_values_in_pmi_range(self):
        s = pmi.get_manufacturing_pmi(first_year="2024")
        assert all(30 < v < 70 for v in s.values)


class TestNonManufacturingPmi:
    def test_returns_monthly_series(self):
        s = pmi.get_non_manufacturing_pmi()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_values_in_pmi_range(self):
        s = pmi.get_non_manufacturing_pmi(first_year="2024")
        assert all(30 < v < 70 for v in s.values)


class TestCompositePmi:
    def test_returns_monthly_series(self):
        s = pmi.get_composite_pmi()
        assert isinstance(s, pd.Series)
        assert s.index.freqstr == "M"

    def test_values_in_pmi_range(self):
        s = pmi.get_composite_pmi(first_year="2024")
        assert all(30 < v < 70 for v in s.values)
