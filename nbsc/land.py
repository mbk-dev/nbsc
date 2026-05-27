import pandas as pd

today_year = pd.Timestamp.today().strftime("%Y")



def get_land_space_purchased_accumulated(first_year: str = "2000", last_year: str = "2023") -> pd.Series:
    """
    Development and Sales of Real Estate, Land Space Purchased, Accumulated (10000 sq.m). Available data range: 2000-2023.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")


def get_land_space_growth_rate(first_year: str = "2000", last_year: str = "2022") -> pd.Series:
    """
    Development and Sales of Real Estate, Land Space Purchased, Accumulated Growth Rate (%). Available data range: 2000-2022.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")


def get_land_transaction_value_accumulated(first_year: str = "2004", last_year: str = "2022") -> pd.Series:
    """
    Development and Sales of Real Estate, Transaction Value of Land, Accumulated (100 million yuan). Available data range: 2004-2022.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")


def get_land_transaction_growth_rate(first_year: str = "2005", last_year: str = "2022") -> pd.Series:
    """
    Development and Sales of Real Estate, Transaction Value of Land, Accumulated Growth Rate (%). Available data range: 2005-2022.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")
