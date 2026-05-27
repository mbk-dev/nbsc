import pandas as pd


def get_auto_retail_current(first_year: str = "2001") -> pd.Series:
    """
    Retail Sales of Enterprises above Designated Size, Automobile, Current Period (100 million yuan). Available data range: 2001+.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")


def get_auto_retail_accumulated(first_year: str = "2001") -> pd.Series:
    """
    Retail Sales of Enterprises above Designated Size, Automobile, Accumulated (100 million yuan). Available data range: 2001+.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")


def get_auto_retail_growth_rate(first_year: str = "2001") -> pd.Series:
    """
    Retail Sales of Enterprises above Designated Size, Automobile, Accumulated (The same period last year=100) (%). Available data range: 2001+.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")


def get_auto_retail_accumulated_growth_rate(first_year: str = "2001") -> pd.Series:
    """
    Retail Sales of Enterprises above Designated Size, Automobile, Accumulated Growth Rate (%). Available data range: 2001+.
    """
    raise NotImplementedError("nbsc 0.2.0: this series is awaiting port to the new NBS API")
