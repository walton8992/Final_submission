# -*- coding: utf-8 -*-
"""
Loading models one by one from ruptures package - not ensembling 
@author: Alex
"""
from datetime import timedelta
import numpy as np
import ruptures as rpt
from ruptures.metrics import randindex
import plotly.express as px
import pandas as pd

def model(search_algo,model_type,tuple_data,sensitivity,dict_sites_melt,min_step,penalty_val=None,hour_limit=None):
    location,variable=tuple_data
    data=dict_sites_melt[location].copy(deep=True)
    data_test=data.copy(deep=True)
    data_test=data[data.variable==variable]
    # 24 hour window
    if hour_limit is not None:
        hour_zero=data_test.iloc[-1:].datetime.iloc[0]
        hour_lookback=hour_zero-timedelta(hours=hour_limit)
        data_test=data_test[data_test.datetime > hour_lookback]
    y=data_test[['datetime','value']]
    y=y.set_index('datetime')
    y=np.array(y['value'].tolist())
    x=data_test['datetime']
    if search_algo=='BottomUp':
        model=rpt.BottomUp(model=model_type,min_size=min_step).fit(y)
    if search_algo=='Pelt':
           model=rpt.Pelt(model=model_type,min_size=min_step).fit(y)
    if search_algo=='Kernal':
              model=rpt.KernelCPD(kernel=model_type,min_size=min_step).fit(y)
    if search_algo=='Window':
               model=rpt.Window(model=model_type,min_size=min_step).fit(y)
 
    algo=model
    if sum(y)==0:
        pass          
    x=np.array(x.tolist()).reshape(-1,1)[~np.isnan(y)]
    y=y[~np.isnan(y)]
    y_shape=y.reshape(-1,1)
    T, d = y_shape.shape  # number of samples, dimension
    pv=((0.25*T)**(1-sensitivity) )*2*np.log(T)
    penalty=pv if penalty_val is None else penalty_val
    change_location = algo.predict(pen=penalty)
    if len(change_location)==0:
        pass
    else:
        # dict_results[location][variable]=datetime_x_values
        return (tuple_data,change_location)
    

     
