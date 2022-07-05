# -*- coding: utf-8 -*-
"""
utility helper for loading/saving and plotting


"""

import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from itertools import cycle
# from ruptures.utils import pairwise
from itertools import tee
import itertools
import pandas as pd
import bz2
import pickle
import os
import shutil


def load_data(filename):
    dictionary = bz2.BZ2File(f'{filename}.pbz2', 'rb')
    dict_sites_melt = pickle.load(dictionary)
    return dict_sites_melt

def delete_folder(path):

    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
            
def save_data(file,filename):
    with bz2.BZ2File(f'{filename}.pbz2', 'w') as f:
        pickle.dump(file, f)
        
        
def plot_change_points_pyplot(data_test,dict_sites_melt,file_location_save =None,save_fig=False,show_fig=False):
    for key,data in data_test.items():
        # for cost,points in data.items():
            y_sns=dict_sites_melt[key][['datetime','value','variable']]
          
            for cost,date in data.items():
                if len(date)==1:
                    pass
                else:
                    fig = px.line(y_sns, x="datetime", y="value",color='variable',title=key+'_'+cost)
                    for x in date:
                      
                        
                            date_plot=y_sns['datetime'][x-1]
                            fig.add_vline(date_plot,line_width=2, line_dash='dash',line_color='red')
                    if show_fig:
                        fig.show()
                    if save_fig:
                        fig.write_html(file_location_save+"/{}_plot.html".format(key+'_'+cost))


def plot_changepoints(flattened_dict,dict_sites_melt,save_loc):
    for key,data in flattened_dict.items():
        y_sns=dict_sites_melt[key][['datetime','value','variable']]
        
        # fig=sns.lineplot(x='datetime',y='value',hue='variable',data=y_sns,ax=ax).set(title=key)
        values=list(itertools.chain(*data.values()))
        if len(values) <=1:
            pass
        else:
            fig,ax=plt.subplots(figsize=(20,20))
            sns.lineplot(x='datetime',y='value',hue='variable',data=y_sns,ax=ax).set(title=key)
            for location in data.values():
                for x in location:
                    x_plot=y_sns['datetime'][x-1]
                    plt.axvline(x_plot,lw=2, color='black',linestyle='--')
            plt.savefig(save_loc+'/{}.jpeg'.format(key))
            plt.close()

def plot_change(flattened_dict,dict_sites_melt):
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
        for key, data in flattened_dict.items():
            x=np.array(dict_sites_melt[key]['datetime']).reshape(-1,1)
            y=dict_sites_melt[key][['value','variable']]
            cpd = list(data['all'])
            if len(cpd)==0:
                pass
            else:
                #unflatten variables
                #change y to each parameter
                
                df_unmelt=pd.DataFrame()
                for variable in y.variable.unique():
                    temp_df=y[y.variable ==variable]
                    df_unmelt=pd.concat([df_unmelt,temp_df],axis=1)
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
                    
def generate_tuple_data(melted_dict):
        
    example_list=example_list=[x for x in melted_dict.keys()]
    variables = ['BElarge','BEsmall','EFlarge','EFsmall']
    tuple_arguments=[(x,y) for x in example_list for y in variables]
    return tuple_arguments

def change_working_dir(new_dir:str) -> print:
    '''
    if working directory not the the argument give, changes to it the enew_dir
    '''
    current_dir=os.getcwd()
    
    print("current working directory ", current_dir)
    if current_dir != new_dir:
        os.chdir(f"{new_dir}")
        print("Changing to : ",os.getcwd())
        
def combine(dict):
    '''
    

    Parameters
    ----------
    dict : Type:dictionary
    Returns
    -------
    new_combined_dict : a dictionary of flattened variabled (belarge,besmall)
    under one dictionary to capture all change points
    
    '''
    new_combined_dict={}
    for name,dic2 in dict.items():
       new_combined_dict[name]={}
       new_combined_dict[name]['all']=[]
       for cost,list_cp in dic2.items():
            list_cp_unique=list(set(list_cp))
          
            # if len(list_cp_unique)>1:
            if name not in new_combined_dict:
                new_combined_dict[name]['all']=list_cp_unique
            else:
                new_combined_dict[name]['all']+=list_cp_unique
       new_combined_dict[name]['all']=list(set(new_combined_dict[name]['all']))
    return new_combined_dict