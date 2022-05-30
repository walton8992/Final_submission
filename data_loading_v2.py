# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:09:49 2022

Practicum Ping Data 

@author: Alex
"""
#%% libraries
import os
import pandas as pd
import sqlite3
import seaborn as sns
import pickle
import bz2
import plotly.express as px
import plotly.io as pio
import numpy as np
pio.renderers.default='browser'
save=False
load=True
#%% change dir
print("current working directory", os.getcwd())
os.chdir(r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Practicum 2022")
print("Changing to : ",os.getcwd())
#%% get data
# loading in modules
#fix if error in db
# https://sqliteviewer.com/blog/database-disk-image-malformed/
if not load:
    conn = sqlite3.connect('ping_practicum.db')
    c = conn.cursor()
    table = pd.read_sql_query("SELECT * from {}".format("ping"), conn)
    conn_2= sqlite3.connect('anomaly.db')
    c_2 = conn_2.cursor()
    location_data = pd.read_sql_query("SELECT * from {}".format("input_to_map"), conn_2)[['latitude','longitude']]
    
if save:
    with bz2.BZ2File('raw_data.pbz2', 'w') as f:
        pickle.dump(table, f)

if load:
    table = bz2.BZ2File('raw_data.pbz2', 'rb')
    table = pickle.load(table)
    location_data = pd.read_csv("site locations.csv")[['latitude','longitude']]
    
#%% EDA
list_sites=list(table.name.unique())
def create_dictionary(melt:bool) -> dict:
    #turn into dict
    dict_test={}
    for name in list_sites:
        dict_test[name]=table[table.name==name]
        dict_test[name].loc[:,'datetime']=pd.to_datetime(dict_test[name].datetime)
        if melt:
            dict_test[name]=dict_test[name].melt(id_vars=['name','datetime'])
    return dict_test
if save:
    dict_sites=create_dictionary(False)
    dict_sites_melt=create_dictionary(True)
    with bz2.BZ2File('site_data.pbz2', 'w') as f:
        pickle.dump(dict_sites, f)
    with bz2.BZ2File('site_data_melted.pbz2', 'w') as f:
        pickle.dump(dict_sites_melt, f)
        
if load:
    dict_sites = bz2.BZ2File('site_data.pbz2', 'rb')
    dict_sites = pickle.load(dict_sites)
    
    dict_sites_melt = bz2.BZ2File('site_data_melted.pbz2', 'rb')
    dict_sites_melt = pickle.load(dict_sites_melt)
#%% change detection
import changefinder
from scipy import stats
from ThymeBoost import ThymeBoost as tb
boosted_model = tb.ThymeBoost()
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict
def changeFinderALLData(data, r, order, smooth):
    cf = changefinder.ChangeFinder(r=r, order=order, smooth=smooth)
    scores = [cf.update(p) for p in data]
    return scores
dict_output=defaultdict(dict)
def create_thymeBoost_graphs(plot=False,save=False):
    model_list=['EFsmall','BEsmall','EFlarge','BElarge']
    for key, data in tqdm( dict_sites.items()):
        for model in model_list:
            ent1=data[['datetime',model]]
            if plot:
                import os
                data_plot=dict_sites_melt[key]
            
                if not os.path.exists("plots"):
                    print("making folder")
                    os.mkdir("plots")
                fig = px.line(data_plot, x="datetime", y="value", color='variable')
                fig.write_html("plots/{}_plot.html".format(key))
            y=np.array(ent1.copy(deep=True)[[model]])
            y=y.ravel()
            if sum(y) > 0:
                boosted_model = tb.ThymeBoost()
                output = boosted_model.detect_outliers(y,
                                                       trend_estimator='linear',
                                                       seasonal_estimator='fourier',
                                                       seasonal_period=25,
                                                       global_cost='maicc',
                                                       fit_type='global')
                dict_output[key][model]=output
                
            else:
                dict_output[key][model]=0
    if save:
        with bz2.BZ2File('thyme_boost_model.pbz2', 'w') as f:
            pickle.dump(dict_output, f)
    
if not load:        
    create_thymeBoost_graphs()
elif load:
    dict_output = bz2.BZ2File('thyme_boost_model.pbz2', 'rb')
    dict_output = pickle.load(dict_output)
     

#%% Ruptures change detection

import ruptures as rpt
data=dict_sites_melt['Sunset Crater'].copy(deep=True)
data_test=data[data.variable=='BElarge']
y=data_test[['datetime','value']]
y=y.set_index('datetime')
y=np.array(y['value'].tolist())
# algo=rpt.Dynp(model="l1", jump=1,min_size=10).fit(y)
cost_function_models = ['linear','rbf','cosine']

result_dict=defaultdict(dict)
for model in cost_function_models:
    penalty_cost_list=[1,10,100,200,500]
    for penalty in penalty_cost_list:
        algo_pureC=rpt.KernelCPD(kernel=model,min_size=1).fit(y)
        penalty_value=penalty
        
        result = algo_pureC.predict(pen=penalty_value)
        #plot
        result=[x-1 for x in result] # real location
        # result_dict[model]['index']=result
        #get date of location index
        x=np.array(data_test['datetime'].tolist())
        real_mean_changes=x[result]
        result_dict[model]['datetime']=real_mean_changes    
        fig = px.line(data, x="datetime", y="value")
        for x in real_mean_changes:
            fig.add_vline(x,line_width=0.5, line_dash='dash')
        # y=y.reset_index()
        result_dict[model][penalty]=fig
    # fig.show()
  
    #%%
for fig in result_dict:
    test=result_dict[fig]['fig']
    test.show()
#%%
n_samples, dim, sigma = 1000, 3, 4
n_bkps = 4  # number of breakpoints
signal, bkps = rpt.pw_constant(n_samples, dim, n_bkps, noise_std=sigma)

# detection
algo = rpt.Pelt(model="rbf").fit(signal)
result = algo.predict(pen=10)

# display
rpt.display(signal, bkps, result)
plt.show()

#%%
ent1=test_data[['datetime','EFsmall']]
ent2=test_data[['datetime','BEsmall']]
ds1=test_data[['datetime','EFlarge']]
ds2=test_data[['datetime','BElarge']]
dataplot1 = changeFinderALLData(ent1, r=0.01, order=2, smooth=3) 
dataplot2 = changeFinderALLData(ent2, r=0.01, order=3, smooth=5) 
dataplot3 = changeFinderALLData(ds1, r=0.01, order=2, smooth=5)    
dataplot4 = changeFinderALLData(ds2, r=0.01, order=3, smooth=5)    
stats.describe(dataplot2)    
#%% plot
for key,data in dict_sites_melt.items():
    
    # sns.lineplot(x='datetime',y='value',hue='variable',data=data)
    fig = px.line(data, x="datetime", y="value", color='variable')
    fig.show()
#%%



