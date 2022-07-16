# -*- coding: utf-8 -*-
"""
Live detection case

Use multiple thread and process to speed detection

"""
from utilities import load_data
from CPDE_ensemble import changePoint

dict_sites_melt = load_data("Data/site_data_melted")
window = changePoint(
    model="window",
    pen=20,
    dict_sites_melt=dict_sites_melt,
    cost_function=list(["Min_MinAbs"]),
    lookback_duration=True,
)
