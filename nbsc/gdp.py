import pandas as pd

from nbsc import request_data

today_year = pd.Timestamp.today().strftime("%Y")


def _fetch_quarterly(series: str, first_year: str) -> pd.Series:
    s = request_data.load_nbs_web(
        series=series, periods=f"{first_year}-{today_year}", freq="quarter"
    )
    s = s[s != 0]
    s.index = s.index.to_period("Q")
    return s.sort_index()


def get_gdp_nominal(first_year: str = "1992") -> pd.Series:
    return _fetch_quarterly("GDP_NOMINAL_Q", first_year)


def get_gdp_nominal_cumulative(first_year: str = "1992") -> pd.Series:
    return _fetch_quarterly("GDP_NOMINAL_CUM", first_year)


def get_gdp_real(first_year: str = "2011") -> pd.Series:
    return _fetch_quarterly("GDP_REAL_Q", first_year)


def get_gdp_real_cumulative(first_year: str = "2011") -> pd.Series:
    return _fetch_quarterly("GDP_REAL_CUM", first_year)


def get_gdp_index(first_year: str = "1992") -> pd.Series:
    return _fetch_quarterly("GDP_INDEX_Q", first_year)


def get_gdp_index_cumulative(first_year: str = "1992") -> pd.Series:
    return _fetch_quarterly("GDP_INDEX_CUM", first_year)


def get_gdp_qoq_growth(first_year: str = "2011") -> pd.Series:
    return _fetch_quarterly("GDP_QOQ", first_year)
