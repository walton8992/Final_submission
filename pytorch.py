# -*- coding: utf-8 -*-
"""
pytroh cpde

"""

from TIRE import DenseTIRE as TIRE, utils

import torch
import numpy as np
import matplotlib.pyplot as plt
from utilities import load_data, change_working_dir

# change_working_dir("practicum_2022")
dict_ts = load_data("Data/melted_dict_data/site_data_melted")


# %%
def run_model(site, epoches, title=None):
    """Run pytorch tire model on site location."""
    data = dict_ts[site]
    data_var = data[data.variable == "BElarge"]
    # fig, ax = plt.subplots(figsize=(10, 10))

    # ax.plot(data_var.datetime, data_var.value)
    # plt.title(site)
    # plt.show()
    dim = 1

    ts = np.array(data_var.value)
    ts = ts.reshape(-1, 1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TIRE(dim).to(device)

    model.fit(ts, epoches=epoches)

    dissimilarities, change_point_scores = model.predict(ts)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(dissimilarities)
    if not title:
        plt.title(site + "_dissimilarity plot")
    else:
        plt.title(title)

    mean_diss = np.mean(dissimilarities)
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.plot(data_var.datetime, data_var.value)
    time = data_var.datetime[19:-20]
    from scipy.signal import find_peaks

    min_diss = min(dissimilarities)
    max_diss = max(dissimilarities)

    peaks, _ = find_peaks(
        dissimilarities, prominence=(max_diss / 10, max_diss)
    )
    # max_peaks =dissimilarities.argsort()[-3:]
    # peaks=utils.find_peaks(dissimilarities)[0]
    # peak_prom=utils.peak_prominences(dissimilarities,peaks)[0]
    # peaks_prom_all = np.array(utils.new_peak_prominences(dissimilarities)[0])

    for iloc, location in enumerate(peaks):

        time_loc = time.iloc[location]
        plt.axvline(time_loc, lw=2, color="black", linestyle="--")
    return dissimilarities


# %%
cuba = run_model("Cuba_1900", 30)
ely_east = run_model("Ely East-10619", 1)
moore = run_model("Moore Ranch", 3)


# HELP increase epcoch increases sens
