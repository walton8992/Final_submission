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


def load_data_pbz(filename):
    dictionary = bz2.BZ2File(f'{filename}.pbz2', 'rb')
    dict_sites_melt = pickle.load(dictionary)
    return dict_sites_melt
#%%
        # ax.set_title
dict_sites_melt=data_load.load_data('site_data_melted')
binseg_flat=load_data_pbz('practicum_2022/Results/binseg_full_flat')
window_flat=load_data_pbz('practicum_2022/Results/window_full_flat')

#%% plotting

utilities.plot_change_points_pyplot(binseg_flat, dict_sites_melt,file_location_save='plots/binseg',save_fig=True)
utilities.plot_change_points_pyplot(window_flat, dict_sites_melt,file_location_save='plots/window',save_fig=True)

#%%

utilities.plot_changepoints(window_flat,dict_sites_melt)