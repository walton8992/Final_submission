# -*- coding: utf-8 -*-
"""
pytroh cpde

"""

from TIRE import DenseTIRE as TIRE, utils
import logging
import torch
import numpy as np
import matplotlib.pyplot as plt
from utilities import load_data, change_working_dir
import pandas as pd
from scipy.signal import find_peaks, peak_prominences, peak_widths
from datetime import timedelta
import itertools
from tqdm import tqdm

# change_working_dir("practicum_2022")
import pathlib
import time

dict_ts = load_data("Data/melted_dict_data/site_data_melted")


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


dict_ts_twentyfounr = twentyfour_hours(dict_ts.copy())
save_folder = r"../plots/Autoencoder/"
small_dict = dict(itertools.islice(dict_ts_twentyfounr.items(), 100))

# %%
def run_model(site, epoches, dict_of_data, title=None, make_folder=False):
    """Run pytorch tire model on site location."""
    data = dict_of_data[site]
    variables = list(data.variable.unique())
    fig, ax = plt.subplots(figsize=(10, 10))
    fig2, ax2 = plt.subplots(figsize=(10, 10))
    peaks = {}
    colours = ["r", "b", "g", "orange"]

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

        peaks_temp, peak_values = find_peaks(dissimilarities, width=50)
        peak_prom = peak_prominences(dissimilarities, peaks_temp)[0]

        # outliers 2 std mean
        # peak_prom[peak_prom > (peak_mean +( 5*peak_std))]

        # find peaks that are big

        # CHECK  - ony 1 peak
        if len(peaks_temp) >= 1:

            peak_std = np.std(peak_prom)
            peak_mean = np.mean(peak_prom)
            peaks_temp = peaks_temp[peak_prom > (peak_mean + (3 * peak_std))]

        peaks[var] = peaks_temp

        time = data[data.variable == var].datetime
        if len(peaks_temp) > 1:
            for iloc, location in enumerate(peaks_temp):

                time_loc = time.iloc[location]
                ax2.axvline(time_loc, lw=2, color=colours[i], linestyle="--")
        elif len(peaks_temp) == 0:
            continue
        else:
            try:
                time_loc = time.iloc[peaks_temp]
                ax2.axvline(time_loc, lw=2, color=colours[i], linestyle="--")
            except:
                logging.warning("error in 1d plot")
                print("cant plot")
    ax.legend()
    ax2.legend()
    if not title:

        ax.set_title(site + "_dissimilarity plot")
        ax2.set_title(site)
    else:
        ax.set_title(title)
    fig.savefig(save_folder + f"/{site}_dissimilarities.png")
    fig2.savefig(save_folder + f"/{site}.png")
    if make_folder:
        path = pathlib.Path(save_folder + f"/{site}")
        path.mkdir(parents=True, exist_ok=True)

        fig.savefig(str(path) + f"/{site}_dissimilarities.png")
        fig2.savefig(str(path) + f"/{site}.png")

    return peaks


#%%
if __name__ == "__main__":
    dict_results = {}
    start_time = time.time()

    for mbile_site in small_dict:
        dict_results[mbile_site] = run_model(mbile_site, 1, dict_ts)
    end_time = time.time()
    total_time = end_time - start_time

    # %%
    # %%
    dict_empty = {}
    for x, y in dict_results.items():
        for a, b in y.items():
            if len(b) != 0:
                if x not in dict_empty:
                    dict_empty[x] = [list(b)]
                else:
                    dict_empty[x].append(list(b))
