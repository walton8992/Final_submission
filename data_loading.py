# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 10:14:40 2022

@author: Alex
"""



import pandas as pd
import sqlite3
import pickle
import bz2
import plotly.io as pio

import matplotlib.pyplot as plt

DATA_FOLDER='Data/'
pio.renderers.default='browser'


    

#% get data
# loading in modules
#fix if error in db
# https://sqliteviewer.com/blog/database-disk-image-malformed/

def get_data_SQL(name_database):
    '''
    

    Parameters
    ----------
    name_database : Str
        DESCRIPTION.  - name of db to open

    Returns
    -------
    table : TYPE
        DESCRIPTION.

    '''
    conn = sqlite3.connect(DATA_FOLDER+f'{name_database}.db')
    c = conn.cursor()
    table = pd.read_sql_query("SELECT * from {}".format("ping"), conn)
    return table

def get_location_Data(name_file):
    location_data = pd.read_csv(DATA_FOLDER+f"{name_file}.csv")
    return location_data
def create_dictionary(melt:bool,table:pd.DataFrame) -> dict:
    list_sites=list(table.name.unique())

    #turn into dict
    dict_test={}
    for name in list_sites:
        dict_test[name]=table[table.name==name]
        dict_test[name].loc[:,'datetime']=pd.to_datetime(dict_test[name].datetime)
        if melt:
            dict_test[name]=dict_test[name].melt(id_vars=['name','datetime'])
    return dict_test

def load_data_pbz(filename):
    dictionary = bz2.BZ2File(DATA_FOLDER+f'{filename}.pbz2', 'rb')
    dict_sites_melt = pickle.load(dictionary)
    return dict_sites_melt

def create_data():
    ping_data=get_data_SQL('ping_practicum')
    location_data=get_location_Data('site locations')
    dict_sites_melt=create_dictionary(True,ping_data)
    return ping_data,location_data,dict_sites_melt

def load_data(filename):
    dict_sites_melt=load_data_pbz(f'{filename}')
    return dict_sites_melt

def save_data(file,filename):
    with bz2.BZ2File(DATA_FOLDER+f'{filename}.pbz2', 'w') as f:
        pickle.dump(file, f)
def create_new_data(save:bool):
    test_data_1=get_data_SQL('Test_Data/CR-pingplot')
    test_data_2=get_data_SQL('Test_Data/LV-pingplot')
    #merge and melt
    test_data=pd.concat([test_data_1,test_data_2])
    test_data_melt=create_dictionary(True, test_data)
    if save:
        save_data(test_data_melt,'test_site_data_melted')
    return test_data_melt

def plot_change_points(ts,ts_change_loc,title=None):
    plt.figure(figsize=(16,4))
    plt.plot(ts)
    for x in ts_change_loc:
        plt.axvline(x,lw=2, color='red')
    plt.title(title)
    plt.show()

def generate_tuple_data(melted_dict):
        
    example_list=example_list=[x for x in melted_dict.keys()]
    variables = ['BElarge','BEsmall','EFlarge','EFsmall']
    tuple_arguments=[(x,y) for x in example_list for y in variables]
    return tuple_arguments
