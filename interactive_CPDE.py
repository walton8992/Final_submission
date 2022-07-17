# -*- coding: utf-8 -*-
"""
Dashboard to show cpd results in interactive table with plots

@author: Alex
"""
from utilities import load_data
import Plotting
from dash import Dash, dash_table
import pandas as pd
import collections

data = Plotting.load_list_data("Results/test_data/Window_all/")
clean_data = dict(Plotting.remove_unuseful_plots(data))
Function = "Max_Rank"

# %%
# test=[(x,y) for x,y in clean_data.items()]
t2 = dict(
    (x, s)
    for x, y in clean_data.items()
    for r, s in y.items()
    if r == Function
)

new_dict = {}
for x, y in clean_data.items():
    for cost, data in y.items():
        if cost == Function:
            new_dict[x] = data
# t2 =list(test[0])
