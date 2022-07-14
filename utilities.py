# -*- coding: utf-8 -*-
"""
utility helper for loading/saving and plotting


"""

import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from itertools import cycle
import time

# from ruptures.utils import pairwise
from itertools import tee
import itertools
import pandas as pd
import bz2
import pickle
import os
import shutil
import plotly.io as pio

pio.renderers.default = "browser"


def dict_combine_cpde(list_cp, combine=False):
    """Get all from list of tuples to dict.

    This should return dict in format of each site,
    each variable and then each cpde detected for that variable

    Returns:
        -dict
    """
    test = {}
    for name, dic in list_cp:
        if name not in test.keys():
            test[name] = dic
        else:
            list_dic = list(dic.items())
            for item in list_dic:
                # HINT item here is a tuple of
                # variable and the cost function cPD detected

                test[name][item[0]] = item[1]

    return test


def flatten_dict_all(dictionary_results: dict):
    """Flatten dict one stage further.

    We want to be able to flatten to see,
    for each of the cost functions, what cpde we get
    and then compare each method with graphs.

    Args:
        -dict

    Returns:
            -dict
    """
    new_dict = {}
    for site, feature_var in dictionary_results.items():
        new_dict[site] = {}
        list_of_features = list(feature_var.keys())
        for feature in list_of_features:
            data = feature_var[feature]
            for cost, changepoint in data.items():
                if cost not in new_dict[site]:

                    new_dict[site][cost] = changepoint
                else:
                    new_dict[site][cost] = list(
                        set(changepoint + new_dict[site][cost])
                    )

    return new_dict


def timethis(func):
    """wrapper to time how long module takes"""

    def wrapper(*args, **kwargs):

        start = time.time()
        functions = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {round(end-start,2)} s")

        return functions

    return wrapper


@timethis
def load_data(filename):
    dictionary = bz2.BZ2File(f"{filename}.pbz2", "rb")
    dict_sites_melt = pickle.load(dictionary)
    return dict_sites_melt


def delete_folder(path):

    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def save_data(file, filename):
    with bz2.BZ2File(f"{filename}.pbz2", "w") as f:
        pickle.dump(file, f)


def plot_change_points_pyplot(data_test, dict_sites_melt, **kwargs):
    # check kwargs savefig
    if kwargs:
        if kwargs.get("save_fig"):
            if not isinstance(kwargs.get("file_location_save"), str):
                raise Exception("String needed to save file down")

    for key, data in data_test.items():
        # for cost,points in data.items():
        y_sns = dict_sites_melt[key][["datetime", "value", "variable"]]

        for cost, date in data.items():
            if len(date) == 1:
                pass
            else:
                if kwargs:
                    title = kwargs.get("title")
                    if title:
                        fig = px.line(
                            y_sns,
                            x="datetime",
                            y="value",
                            color="variable",
                            title=key + "_" + title,
                        )

                else:
                    fig = px.line(
                        y_sns,
                        x="datetime",
                        y="value",
                        color="variable",
                        title=key + "_" + cost,
                    )
                for x in date:

                    date_plot = y_sns["datetime"][x - 1]
                    fig.add_vline(
                        date_plot,
                        line_width=2,
                        line_dash="dash",
                        line_color="red",
                    )
                if kwargs:
                    file_location_save = kwargs.get("file_location_save")
                    save_fig = kwargs.get("save_fig")
                    show_fig = kwargs.get("show")
                    if show_fig:
                        fig.show()
                        # fig.show(renderer="svg")

                    if save_fig:
                        if kwargs:
                            title = kwargs.get("title")
                            if title:
                                # fig.write_html(file_location_save+"/{}_plot.html".format(key+'_'+title))
                                fig.write_image(
                                    file_location_save
                                    + "/{}_plot.png".format(key + "_" + title)
                                )
                        else:
                            fig.write_html(
                                file_location_save
                                + "/{}_plot.html".format(key + "_" + cost)
                            )


def plot_changepoints(flattened_dict, dict_sites_melt, save_loc):
    for key, data in flattened_dict.items():
        y_sns = dict_sites_melt[key][["datetime", "value", "variable"]]

        # fig=sns.lineplot(x='datetime',y='value',hue='variable',data=y_sns,ax=ax).set(title=key)
        values = list(itertools.chain(*data.values()))
        if len(values) <= 1:
            pass
        else:
            fig, ax = plt.subplots(figsize=(20, 20))
            sns.lineplot(
                x="datetime", y="value", hue="variable", data=y_sns, ax=ax
            ).set(title=key)
            for location in data.values():
                for x in location:
                    x_plot = y_sns["datetime"][x - 1]
                    plt.axvline(x_plot, lw=2, color="black", linestyle="--")
            plt.savefig(save_loc + "/{}.jpeg".format(key))
            plt.close()


def plot_change(flattened_dict, dict_sites_melt):
    """


    Parameters
    ----------
    x : TYPE
        array of datetime values.
    y : TYPE
        array of value pings.
    cpd : TYPE
        array of cpd in location (not datetime) format.
    ax : TYPE
        axes to plt ont.

    Returns
    -------
    None.

    """
    for key, data in flattened_dict.items():
        x = np.array(dict_sites_melt[key]["datetime"]).reshape(-1, 1)
        y = dict_sites_melt[key][["value", "variable"]]
        cpd = list(data["all"])
        if len(cpd) == 0:
            pass
        else:
            # unflatten variables
            # change y to each parameter

            df_unmelt = pd.DataFrame()
            for variable in y.variable.unique():
                temp_df = y[y.variable == variable]
                df_unmelt = pd.concat([df_unmelt, temp_df], axis=1)
            n_samples, n_features = np.array(y).reshape(-1, 1).shape
            COLOR_CYCLE = ["#4286f4", "#f44174"]

            color_cycle = cycle(COLOR_CYCLE)
            # plot s
            ax.plot(range(n_samples), y)

            # color each (true) regime
            bkps = [0] + sorted(cpd)
            alpha = 0.2  # transparency of the colored background
            # store list as iterators
            l1, l2 = tee(bkps)
            next(l2, None)
            zipped_lists = zip(l1, l2)
            for (start, end), col in zip(zipped_lists, color_cycle):
                ax.axvspan(
                    max(0, start - 0.5), end - 0.5, facecolor=col, alpha=alpha
                )


def generate_tuple_data(melted_dict):

    example_list = example_list = [x for x in melted_dict.keys()]
    variables = ["BElarge", "BEsmall", "EFlarge", "EFsmall"]
    tuple_arguments = [(x, y) for x in example_list for y in variables]
    return tuple_arguments


def change_working_dir(new_dir: str) -> print:
    """
    if working directory not the the argument give, changes to it the enew_dir
    """
    current_dir = os.getcwd()

    print("current working directory ", current_dir)
    if current_dir != new_dir:
        os.chdir(f"{new_dir}")
        print("Changing to : ", os.getcwd())


def combine(dict):
    """


    Parameters
    ----------
    dict : Type:dictionary
    Returns
    -------
    new_combined_dict : a dictionary of flattened variabled (belarge,besmall)
    under one dictionary to capture all change points

    """
    new_combined_dict = {}
    for name, dic2 in dict.items():
        new_combined_dict[name] = {}
        new_combined_dict[name]["all"] = []
        for cost, list_cp in dic2.items():
            list_cp_unique = list(set(list_cp))

            # if len(list_cp_unique)>1:
            if name not in new_combined_dict:
                new_combined_dict[name]["all"] = list_cp_unique
            else:
                new_combined_dict[name]["all"] += list_cp_unique
        new_combined_dict[name]["all"] = list(
            set(new_combined_dict[name]["all"])
        )
    return new_combined_dict
