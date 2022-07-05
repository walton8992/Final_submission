# -*- coding: utf-8 -*-
"""
load and plot data generate from Pracitcum Class

@author: Alex
"""
#%% library import 
import utilities
from utilities import load_data ,delete_folder
import collections
import Practicum_2022
dict_sites_melt=load_data('Data/site_data_melted')
binseg,binseg_flat,window,window_flat=Practicum_2022.load()
#%% clear folders of old plots

delete_folder('plots/binseg/pyplot')
delete_folder('plots/binseg/matplotlib')
delete_folder('plots/window/pyplot')
delete_folder('plots/window/matplotlib')


#%%
def remove_unuseful_plots(dictionary:dict):
    '''
    Want to remove those with just end plot'''
   
    new_dict=collections.defaultdict(dict)
    plot_dict=dictionary
    for key,item in plot_dict.items():
        if len (list(item.values())[0])==1:
            pass
        else:
            new_dict[key] = item
    return new_dict
#%%plot
dict_real=remove_unuseful_plots(window_flat)
utilities.plot_change_points_pyplot(binseg_flat, dict_sites_melt,file_location_save='plots/binseg/pyplot',save_fig=True)
utilities.plot_change_points_pyplot(window_flat, dict_sites_melt,file_location_save='plots/window/pyplot',save_fig=True)
utilities.plot_changepoints(binseg_flat,dict_sites_melt,save_loc='plots/binseg/matplotlib')
utilities.plot_changepoints(window_flat,dict_sites_melt,save_loc='plots/window/matplotlib')
