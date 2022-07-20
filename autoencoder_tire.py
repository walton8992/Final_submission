"""
implementation of the TIRE model referenced in the paper

"""

from TIRE import DenseTIRE as TIRE
import logging
import torch
import numpy as np
import matplotlib.pyplot as plt
from utilities import load_data
from scipy.signal import find_peaks, peak_prominences
from datetime import timedelta
import itertools
import pathlib
import time

dict_ts = load_data("Data/melted_dict_data/site_data_melted")


def twentyfour_hours(dictionary: dict):
    """
    Reduct time to twentfour hours.

    Parameters
    ----------
    dictionary : dict
        a dictionary in form of melted sites.

    Returns
    -------
    dictionary : dict
        a dictionary in the same format as the melted sites, but only 24 hour lookback.

    """
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


def run_model(
    site: str, epoches: int, dict_of_data: dict, title=None, make_folder=False
):
    """
    Run pytorch tire model on site location.
    The threshold is set to 3xstd for testing.
    Plots are saved in a location, with an arugment to make a folder for plots.

    Parameters
    ----------
    site : str
        string of site.
    epoches : int
        number of Epochs for Autoencoder method.
    dict_of_data : dict
        a dictionary, in the formal of the site_melted_date format.
    title : str, optional
        Title for plots. The default is None.
    make_folder : Boolean, optional
        Bool to signify if folder is wanted ot be created. The default is False.

    Returns
    -------
    peaks : dict
        dictory of peaks with key being mobile site.

    """

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

        # outliers 3 std mean
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


def main():
    """
    Code to implrement TIRE model refernced in the project.

    Returns
    -------
    dict_results : dict
        A dictionary of all results for each site and each variable
    dict_empty : dict
        A combined dictionary - this is only those sites that a changepoint has been detected.

    """
    dict_results = {}
    start_time = time.time()
    for mbile_site in dict_ts:
        dict_results[mbile_site] = run_model(mbile_site, 1, dict_ts)
    end_time = time.time()
    total_time = end_time - start_time
    dict_empty = {}
    for x, y in dict_results.items():
        for a, b in y.items():
            if len(b) != 0:
                if x not in dict_empty:
                    dict_empty[x] = [list(b)]
                else:
                    dict_empty[x].append(list(b))
    return dict_results, dict_empty


#%%
if __name__ == "__main__":

    main()
