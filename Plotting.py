# -*- coding: utf-8 -*-
"""
load and plot data generate from Pracitcum Class

@author: Alex
"""
#%% library import 

import os
current_do=os.getcwd()
os.chdir(r'C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final')
import utilities
import data_loading as data_load
import os
from utilities import load_data_pbz ,delete_folder



     
#%%load

dict_sites_melt=data_load.load_data('site_data_melted')
binseg_flat=load_data_pbz('practicum_2022/Results/binseg_flat_24')
window_flat=load_data_pbz('practicum_2022/Results/window_flat_24')

#%% clear folder
delete_folder('plots/binseg/pyplot')
delete_folder('plots/binseg/matplotlib')
delete_folder('plots/window/pyplot')
delete_folder('plots/window/matplotlib')

#%%plot
utilities.plot_change_points_pyplot(binseg_flat, dict_sites_melt,file_location_save='plots/binseg/pyplot',save_fig=True)
utilities.plot_change_points_pyplot(window_flat, dict_sites_melt,file_location_save='plots/window/pyplot',save_fig=True)
#%%
utilities.plot_changepoints(binseg_flat,dict_sites_melt,save_loc='plots/binseg/matplotlib')
utilities.plot_changepoints(window_flat,dict_sites_melt,save_loc='plots/window/matplotlib')