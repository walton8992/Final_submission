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
import Practicum_2022
import one_model_test
import time
import plotly.io as pio
import os

pio.renderers.default = "browser"
dict_sites_melt = load_data("Data/site_data_melted")
list_old_models = one_model_test.load()


def clear_folder_plots():
    """To clear folder of plots quickly."""
    delete_folder("plots/binseg/pyplot")
    delete_folder("plots/binseg/matplotlib")
    delete_folder("plots/window/pyplot")
    delete_folder("plots/window/matplotlib")


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


def load_main_data():
    """Load main data for 5 test models."""
    dict_total = {}
    for filename in os.listdir(r"practicum_2022/Results/main_data"):
        file = load_data(r"practicum_2022/Results/main_data/" + filename[:-5])
        file_combined = dict_combine_cpde(file)
        file_flat = flatten_dict_all(file_combined)
        dict_total = {**dict_total, **file_flat}
    return dict_total


def load_list_data():
    """Load data from test_data folder.

    This is the folder that has all cost functions

    returns: dict
    """
    dict_total_list = {}
    for filename in os.listdir(r"practicum_2022/Results/test_data"):
        file = load_data(r"practicum_2022/Results/test_data/" + filename[:-5])
        file_dict = dict_combine_cpde(file, combine=False)
        dict_2 = flatten_dict_all(file_dict)
        for key, item in dict_2.items():
            dict_total_list[key] = item

    return dict_total_list


main_dict = load_main_data()
test_dict = load_list_data()

# %% loading model examples


model1 = list_old_models[0]
model2 = list_old_models[5]
model3 = list_old_models[6]
combined_dict = remove_unuseful_plots(combine(model1[1]))
combined_dict_window = remove_unuseful_plots(combine(model2[1]))
combined_dict_window_2 = remove_unuseful_plots(combine(model3[1]))

# %% plotting model 0, model 2 and and model 3
# attempts to noise effects with different settings
with elapsed():
    utilities.plot_change_points_pyplot(
        combined_dict,
        dict_sites_melt,
        show=False,
        title="bottom_up l2",
        save_fig=True,
        file_location_save=r"plots\old_model\bottom_up_l2\\",
    )

with elapsed():
    utilities.plot_change_points_pyplot(
        combined_dict_window,
        dict_sites_melt,
        show=False,
        title="Window rbf. Pen = 0.65",
        save_fig=True,
        file_location_save=r"plots\old_model\window_rbf\\",
    )

with elapsed():
    utilities.plot_change_points_pyplot(
        combined_dict_window_2,
        dict_sites_melt,
        show=False,
        title="Window rbf. Pen = 100",
        save_fig=True,
        file_location_save=r"plots\old_model\window_rbf_100\\",
    )
# %% plot CPDE
# plot graphs from CPDE module

# HINT loading CPDE output here.
binseg, binseg_flat, window, window_flat = Practicum_2022.load_flat()
binseg_flat_final = remove_unuseful_plots(binseg_flat)
window_flat_final = remove_unuseful_plots(window_flat)

#
with elapsed():
    utilities.plot_change_points_pyplot(
        binseg_flat_final,
        dict_sites_melt,
        show=False,
        title="CPDE Binseg Combined",
        file_location_save="plots/binseg/pyplot",
        save_fig=True,
    )

utilities.plot_change_points_pyplot(
    window_flat,
    dict_sites_melt,
    file_location_save="plots/window/pyplot",
    save_fig=True,
)
utilities.plot_changepoints(
    binseg_flat, dict_sites_melt, save_loc="plots/binseg/matplotlib"
)
utilities.plot_changepoints(
    window_flat, dict_sites_melt, save_loc="plots/window/matplotlib"
)
