from nbsc.inflation import (
    get_inflation_from_2001,
    get_recent_inflation,
    get_annual_inflation,
    calculate_monthly_from_annual,
)
from nbsc.gdp import (
    get_gdp_nominal,
    get_gdp_nominal_cumulative,
    get_gdp_real,
    get_gdp_real_cumulative,
    get_gdp_index,
    get_gdp_index_cumulative,
    get_gdp_qoq_growth,
)
from nbsc.pmi import (
    get_manufacturing_pmi,
    get_non_manufacturing_pmi,
    get_composite_pmi,
)
from nbsc.money_supply import (
    get_m2,
    get_m2_yoy,
    get_m1,
    get_m1_yoy,
    get_m0,
    get_m0_yoy,
)
from nbsc.unemployment import get_unemployment_rate
from nbsc.ppi import get_ppi_yoy, get_ppi_mom
from nbsc.household import (
    get_household_appliances_retail_current,
    get_household_appliances_retail_accumulated,
    get_household_appliances_retail_growth_rate,
    get_household_appliances_retail_accumulated_growth_rate,
)
from nbsc.auto_retail import (
    get_auto_retail_current,
    get_auto_retail_accumulated,
    get_auto_retail_growth_rate,
    get_auto_retail_accumulated_growth_rate,
)
from nbsc.investment import (
    get_real_estate_investment_accumulated,
    get_real_estate_investment_growth_rate,
    get_auxiliary_investment_accumulated,
    get_auxiliary_investment_growth_rate,
    get_residential_total_investment_accumulated,
    get_residential_total_investment_growth_rate,
    get_small_housing_investment_accumulated,
    get_small_housing_investment_growth_rate,
    get_large_housing_investment_accumulated,
    get_large_housing_investment_growth_rate,
    get_villa_investment_accumulated,
    get_villa_investment_growth_rate,
    get_office_investment_accumulated,
    get_office_investment_growth_rate,
    get_business_housing_investment_accumulated,
    get_business_housing_investment_growth_rate,
    get_real_estate_other_investment_accumulated,
    get_real_estate_other_investment_growth_rate,
    get_real_estate_construction_investment_accumulated,
    get_real_estate_construction_investment_growth_rate,
    get_real_estate_installation_investment_accumulated,
    get_real_estate_installation_investment_growth_rate,
    get_real_estate_equipment_investment_accumulated,
    get_real_estate_equipment_investment_accumulated_growth_rate,
    get_real_estate_misc_investment_accumulated,
    get_real_estate_misc_investment_agrowth_rate,
    get_land_acquisition_investment_accumulated,
    get_land_acquisition_investment_agrowth_rate,
    get_planned_real_estate_investment_accumulated,
    get_planned_real_estate_growth_rate,
    get_new_fixed_assets_accumulated,
    get_new_fixed_assets_growth_rate
)
from nbsc.land import (
    get_land_space_purchased_accumulated,
    get_land_space_growth_rate,
    get_land_transaction_value_accumulated,
    get_land_transaction_growth_rate,
)
from nbsc.request_data import load_nbs_web
