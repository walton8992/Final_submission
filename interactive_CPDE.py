# -*- coding: utf-8 -*-
"""
Code to run through  generated  CPDE ensemble
@author: Alex
"""
from utilities import load_data, change_working_dir, plot_change_points_pyplot
import Plotting
import collections
import seaborn as sns
import matplotlib.pyplot as plt

change_working_dir(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022"
)
data = Plotting.load_list_data("Results/test_data/Window_all/")
dict_sites_melt = load_data(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022\Data\melted_dict_data\site_data_melted"
)
clean_data = dict(Plotting.remove_unuseful_plots(data))
Function = "Min_MinAbs"
#%%
SCALING_AGGREGATION = [
    "Min_Raw",
    "Min_MinMax",
    "Min_Znorm",
    "Min_MinAbs",
    "Min_Rank",
    "Sum_Raw",
    "Sum_MinMax",
    "Sum_Znorm",
    "Sum_MinAbs",
    "Sum_Rank",
    "WeightedSum_Raw",
    "WeightedSum_MinMax",
    "WeightedSum_Znorm",
    "WeightedSum_MinAbs",
    "WeightedSum_Rank",
    "Max_Raw",
    "Max_MinMax",
    "Max_Znorm" "Max_MinAbs",
    "Max_Rank",
]


def plot(data, Function):
    for key, item in data.items():
        plotting = dict_sites_melt[key]
        fig, ax = plt.subplots(figsize=(20, 20))
        y = sns.lineplot(
            x="datetime", y="value", hue="variable", data=plotting, ax=ax
        )
        # plot changepoints
        y.set_xlabel("Datetime", fontsize=40)
        y.set_ylabel("pingtime [ms]", fontsize=40)
        y.set_title(
            "{}_\n cost_aggregation = {}".format(key, Function),
            fontsize=40,
        )
        for x in item:
            timestamp_x = plotting[
                plotting.variable == "BEsmall"
            ].datetime.iloc[x]
            plt.axvline(x=timestamp_x, color="red", linestyle="--")
        plt.savefig(
            r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\plots\interactive_CPDE\{}_{}.png".format(
                key, Function
            )
        )
        plt.close()

    # %%


# test=[(x,y) for x,y in clean_data.items()]
dict_funct = {}
for Function in SCALING_AGGREGATION:
    dict_cost_norm = dict(
        (x, s)
        for x, y in clean_data.items()
        for r, s in y.items()
        if r == Function
    )

    data_end_removed = {}
    for key, item in dict_cost_norm.items():
        # data is dframe
        temp_list = [x for x in item if x not in [3024, 3025]]
        if not len(temp_list) == 0:
            data_end_removed[key] = temp_list
    dict_funct[Function] = data_end_removed
#%%
for key, item in dict_funct.items():
    plot(data_end_removed, Function)
#%%
