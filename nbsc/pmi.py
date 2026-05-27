import pandas as pd

from nbsc import request_data

today_year = pd.Timestamp.today().strftime("%Y")


def _fetch_monthly(series: str, first_year: str) -> pd.Series:
    s = request_data.load_nbs_web(
        series=series, periods=f"{first_year}-{today_year}", freq="month"
    )
    s = s[s != 0]
    s.index = s.index.to_period("M")
    return s.sort_index()


def get_manufacturing_pmi(first_year: str = "2005") -> pd.Series:
    return _fetch_monthly("PMI_MANUFACTURING", first_year)


def get_non_manufacturing_pmi(first_year: str = "2007") -> pd.Series:
    return _fetch_monthly("PMI_NON_MANUFACTURING", first_year)


def get_composite_pmi(first_year: str = "2017") -> pd.Series:
    return _fetch_monthly("PMI_COMPOSITE", first_year)
