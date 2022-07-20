# -*- coding: utf-8 -*-
"""
Run through and create plots of each site to view if changepoint exists

"""
from utilities import load_data, plot_changepoints
import seaborn as sns
import matplotlib.pyplot as plt

all_data = load_data(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022\Data\melted_dict_data\site_data_melted"
)
#%%

for key, data in all_data.items():
    y_sns = all_data[key][["datetime", "value", "variable"]]
    fig, ax = plt.subplots(figsize=(15, 15))
    fig = sns.lineplot(
        x="datetime", y="value", hue="variable", data=y_sns, ax=ax
    ).set(title=key)
    plt.savefig(r"../plots/all_plots_for_accuracy/ {}.png".format(key))
    plt.close()
    #%%
