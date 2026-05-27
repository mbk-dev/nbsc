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


def get_m2(first_year: str = "1999") -> pd.Series:
    return _fetch_monthly("M2", first_year)


def get_m2_yoy(first_year: str = "1999") -> pd.Series:
    return _fetch_monthly("M2_YOY", first_year)


def get_m1(first_year: str = "1999") -> pd.Series:
    return _fetch_monthly("M1", first_year)


def get_m1_yoy(first_year: str = "1999") -> pd.Series:
    return _fetch_monthly("M1_YOY", first_year)


def get_m0(first_year: str = "1999") -> pd.Series:
    return _fetch_monthly("M0", first_year)


def get_m0_yoy(first_year: str = "1999") -> pd.Series:
    return _fetch_monthly("M0_YOY", first_year)
