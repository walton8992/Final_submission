# -*- coding: utf-8 -*-
"""
load and plot data generate from Pracitcum Class
Both the CPD as well as CPDEmodels
@author: Alex
"""
# %% library import

import utilities
from utilities import (
    load_data,
    delete_folder,
    combine,
    dict_combine_cpde,
    flatten_dict_all,
)
import collections
import one_model_test
import time
import plotly.io as pio
import os


def clear_folder_plots():
    """To clear folder of plots quickly."""
    delete_folder("plots/binseg/pyplot")
    delete_folder("plots/binseg/matplotlib")
    delete_folder("plots/window/pyplot")
    delete_folder("plots/window/matplotlib")
    delete_folder(r"plots\binseg\final_plots")


def remove_unuseful_plots(dictionary: dict):
    """Want to remove those with just line at the end of the plot."""
    new_dict = collections.defaultdict(dict)
    plot_dict = dictionary
    for key, item in plot_dict.items():
        if len(list(item.values())[0]) == 1:
            pass
        else:
            new_dict[key] = item
    return new_dict


class elapsed:
    """Class to time in ms."""

    def __enter__(self):
        """Start time."""
        self.start = time.time()

    def __exit__(self, *args):
        """End time."""
        print("%.1f ms" % ((time.time() - self.start) * 1000))


def load_main_data(file_location):
    """Load main data for 5 test models."""
    dict_total = {}
    for filename in os.listdir(file_location):
        file = load_data(file_location + r"/" + filename[:-5])
        file_combined = dict_combine_cpde(file)
        file_flat = flatten_dict_all(file_combined)
        dict_total = {**dict_total, **file_flat}
    return dict_total


def load_list_data(folder):
    """Load data from test_data folder.

    This is the folder that has all cost functions in many different dicts


    returns: dict
    """
    dict_total_list = {}
    none_dict = {}
    for filename in os.listdir(folder):
        file = load_data(folder + r"/" + filename[:-5])
        if not any(file):  # check if list is none

            none_dict[filename] = file
            continue
        file_dict = dict_combine_cpde(file, combine=False)
        dict_2 = flatten_dict_all(file_dict)
        for key, item in dict_2.items():
            dict_total_list[key] = item

    return dict_total_list


def plot_best_algo(data_input, dict_sites_melt, location, title):
    """Load in dict of each site with all tested cost functions."""
    utilities.plot_change_points_pyplot(
        data_input,
        dict_sites_melt,
        show=False,
        title=title,
        file_location_save=location,
        save_fig=True,
    )


# %% plot CPDE
# plot graphs from CPDE module

# HINT loading CPDE output here.
if __name__ == "__main__":
    print("Main")
    pio.renderers.default = "browser"
    dict_sites_melt = load_data("Data/melted_dict_data/site_data_melted")
    list_old_models = one_model_test.load()
    main_dict = load_main_data("Results/main_data/")

    test_dict = load_list_data("Results/test_data/Window_all/")

    clean_data = remove_unuseful_plots(test_dict)
    #%%
    plot_best_algo(
        clean_data, dict_sites_melt, "../plots/window/final", "window_ALL"
    )
