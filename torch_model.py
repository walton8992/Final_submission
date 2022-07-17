# -*- coding: utf-8 -*-
"""
pytroh cpde

"""

from TIRE import DenseTIRE as TIRE, utils

import torch
import numpy as np
import matplotlib.pyplot as plt
from utilities import load_data, change_working_dir
import pandas as pd
from scipy.signal import find_peaks
from datetime import timedelta
import itertools

# change_working_dir("practicum_2022")
dict_ts = load_data("Data/melted_dict_data/site_data_melted")
import pathlib


def twentyfour_hours(dictionary):

    for key, data in dictionary.items():
        # data_time = data[data]
        hour_zero = data.iloc[-1:].datetime.iloc[0]
        hour_24 = hour_zero - timedelta(hours=24)
        data_test = (
            data[data.datetime > hour_24].reset_index().drop(columns="index")
        )
        dictionary[key] = data_test
    return dictionary


dict_ts_twentyfounr = twentyfour_hours(dict_ts)
save_folder = r"../plots/Autoencoder/"
small_dict = dict(itertools.islice(dict_ts_twentyfounr.items(), 20))

# %%
def run_model(site, epoches, title=None):
    """Run pytorch tire model on site location."""
    data = dict_ts_twentyfounr[site]
    variables = list(data.variable.unique())
    fig, ax = plt.subplots(figsize=(10, 10))
    fig2, ax2 = plt.subplots(figsize=(10, 10))
    peaks = {}
    colours = ["r", "b", "g", "orange"]
    path = pathlib.Path(save_folder + f"/{site}")
    path.mkdir(parents=True, exist_ok=True)

    for i, var in enumerate(variables):
        data_var = data[data.variable == var].value
        dim = 1
        ts = np.array(data_var)
        ts = ts.reshape(-1, 1)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = TIRE(dim).to(device)
        model.fit(ts, epoches=epoches)
        dissimilarities, change_point_scores = model.predict(ts)

        ax.plot(dissimilarities, color=colours[i], label=var)
        main_plot_data = data[data.variable == var][["datetime", "value"]]
        ax2.plot(
            main_plot_data.datetime,
            main_plot_data.value,
            color=colours[i],
            label=var,
        )
        peaks_temp = find_peaks(dissimilarities, width=(150,))[0]
        peaks[var] = peaks_temp
    ax.legend()
    ax2.legend()
    if not title:

        ax.set_title(site + "_dissimilarity plot")
        ax2.set_title(site)
    else:
        ax.set_title(title)
    fig.savefig(save_folder + f"/{site}_dissimilarities.png")
    fig2.savefig(save_folder + f"/{site}.png")
    fig.savefig(str(path) + f"/{site}_dissimilarities.png")
    fig2.savefig(str(path) + f"/{site}.png")

    # mean_diss = np.mean(dissimilarities)
    # fig, ax = plt.subplots(figsize=(10, 10))
    # ax.plot(data_var.datetime, data_var.value)
    # time = data_var.datetime[19:-20]
    # from scipy.signal import find_peaks

    # min_diss = min(dissimilarities)
    # max_diss = max(dissimilarities)

    # peaks, _ = find_peaks(
    #     dissimilarities, prominence=(max_diss / 10, max_diss)
    # )

    # for iloc, location in enumerate(peaks):

    #     time_loc = time.iloc[location]
    #     plt.axvline(time_loc, lw=2, color="black", linestyle="--")
    return peaks


# %%
cuba = run_model("Cuba_1900", 1)
# %%
ely_east = run_model("Ely East-10619", 1)
#%%
moore = run_model("Moore Ranch", 1)
# %%
moore = run_model("Devil's Head-203", 1)

#%%
dict_results = {}
for mbile_site in small_dict:
    dict_results[mbile_site] = run_model(mbile_site, 1)
dict_results["ely"] = run_model("Ely East-10619", 1)
# %%
dict_cost_norm = dict(
    (x, s)
    for x, y in dict_results.items()
    for r, s in y.items()
    if len(s) != 0
)
# get plots in
# HELP increase epcoch increases sens
