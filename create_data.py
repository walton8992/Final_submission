# -*- coding: utf-8 -*-
"""
Script to generate dictionaries from db filees and site location files

@author: Alex
"""

import pandas as pd
import sqlite3


# loading in modules
# fix if error in db
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
    conn = sqlite3.connect(f'{name_database}.db')
    c = conn.cursor()
    table = pd.read_sql_query("SELECT * from {}".format("ping"), conn)
    return table

def get_location_Data(name_file):
    location_data = pd.read_csv(f"{name_file}.csv")
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



def create_new_data(save:bool):
    test_data_1=get_data_SQL('Test_Data/CR-pingplot')
    test_data_2=get_data_SQL('Test_Data/LV-pingplot')
    #merge and melt
    test_data=pd.concat([test_data_1,test_data_2])
    test_data_melt=create_dictionary(True, test_data)
   
    return test_data_melt


def create_data(file_location_database,file_location_sites):
    path=file_location_database+'ping_practicum'
    raw_data=get_data_SQL(path)
    location_data=get_location_Data(file_location_sites+'site locations')
    dict_sites_melt=create_dictionary(True,raw_data)
    return raw_data,location_data,dict_sites_melt

