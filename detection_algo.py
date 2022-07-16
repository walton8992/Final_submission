# -*- coding: utf-8 -*-
"""
Live detection case

Use multiple thread and process to speed detection

"""
from utilities import load_data, change_working_dir
from CPDE_ensemble import changePoint

change_working_dir(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022"
)
dict_sites_melt = load_data(r"Data\melted_dict_data\site_data_melted")
#%%
window = changePoint(
    model="window",
    pen=20,
    dict_sites_melt=dict_sites_melt,
    cost_function=list(["Min_MinAbs"]),
    lookback_duration=True,
)
new_sites = window.dict_sites_melt
