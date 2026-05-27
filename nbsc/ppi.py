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


def get_ppi_yoy(first_year: str = "1996") -> pd.Series:
    return _fetch_monthly("PPI_FACTORY_YOY", first_year)


def get_ppi_mom(first_year: str = "2011") -> pd.Series:
    return _fetch_monthly("PPI_FACTORY_MOM", first_year)
