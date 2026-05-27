import pandas as pd

from nbsc import request_data

today_year = pd.Timestamp.today().strftime("%Y")


def get_unemployment_rate(first_year: str = "2018") -> pd.Series:
    s = request_data.load_nbs_web(
        series="UNEMPLOYMENT", periods=f"{first_year}-{today_year}", freq="month"
    )
    s = s[s != 0]
    s.index = s.index.to_period("M")
    return s.sort_index()
