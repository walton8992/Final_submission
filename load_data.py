# -*- coding: utf-8 -*-
"""
load and plot data generate from Pracitcum Class

@author: Alex
"""
import os
current_do=os.getcwd()
os.chdir(r'C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final')
import utilities
import bz2
import pickle
import data_loading as data_load
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
def load_data_pbz(filename):
    dictionary = bz2.BZ2File(f'{filename}.pbz2', 'rb')
    dict_sites_melt = pickle.load(dictionary)
    return dict_sites_melt


def plot_changepoints(flattened_dict):
    for key,data in flattened_dict.items():
        y_sns=dict_sites_melt[key][['datetime','value','variable']]
        fig,ax=plt.subplots()
        
        sns.lineplot(x='datetime',y='value',hue='variable',data=y_sns,ax=ax).set(title=key)
        
        for location in data.values():
            for x in location:
                x_plot=y_sns['datetime'][x-1]
                plt.axvline(x_plot,lw=2, color='black',linestyle='--')

def plot_change(x,y,cpd,ax):
        '''
    
    
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
    
        '''
        from itertools import cycle
        # from ruptures.utils import pairwise
        from itertools import tee

        n_samples, n_features = np.array(y).reshape(-1,1).shape
        COLOR_CYCLE = ["#4286f4", "#f44174"]

        color_cycle = cycle(COLOR_CYCLE)
        # plot s
        ax.plot(range(n_samples), y)

        # color each (true) regime
        bkps = [0] + sorted(cpd)
        alpha = 0.2  # transparency of the colored background
        #store list as iterators
        l1,l2=tee(bkps)
        next(l2,None)
        zipped_lists=zip(l1,l2)
        for (start,end ),col in zip(zipped_lists,color_cycle):
            ax.axvspan(max(0, start - 0.5), end - 0.5, facecolor=col, alpha=alpha)
        # ax.set_title
dict_sites_melt=data_load.load_data('site_data_melted')

binseg_flat=load_data_pbz('practicum_2022/Results/binseg_full_flat')
window_flat=load_data_pbz('practicum_2022/Results/window_full_flat')

utilities.plot_change_points_pyplot(binseg_flat, dict_sites_melt,file_location_save='plots/binseg',save_fig=True)
utilities.plot_change_points_pyplot(window_flat, dict_sites_melt,file_location_save='plots/window',save_fig=True)
