# -*- coding: utf-8 -*-
"""
Individual model test for hyper parameters (ran this before using multithreading)

@author: Alex
"""


from utilities import save_data,load_data,generate_tuple_data,change_working_dir
change_working_dir(r'C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final')
from tqdm import tqdm
import itertools
from collections import defaultdict
from One_model import models as models
import time
from concurrent.futures import ThreadPoolExecutor
import create_data

class one_Model:
    def __init__(self):
       self.dict_sites_melt=load_data(r'Data/site_data_melted')
       self.location_data=create_data.get_location_Data('Data/site locations')
       self.test_data_melt=load_data('Data/test_site_data_melted')
       self.tuple_arguments=generate_tuple_data(self.dict_sites_melt)
    
    
    
    # tuple_arguments=[x for x in tuple_arguments if x[0] in ['Moore Ranch','Sunset Crater','Eleven Mile']]
    
    def thread_Process_model(self,search_algo,sensitivity_threshold,model,min_step,penalty_val=None,hour_limit=None):
        start=time.time()
    
        with ThreadPoolExecutor(max_workers = 14) as executor:
             results = list(tqdm(executor.map(models.model,
                                 itertools.repeat(search_algo,len(self.tuple_arguments)),
                                 itertools.repeat(model,len(self.tuple_arguments)),
                                 self.tuple_arguments,
                                 itertools.repeat(sensitivity_threshold,len(self.tuple_arguments)),
                                 itertools.repeat(self.dict_sites_melt,len(self.tuple_arguments)),
                                 itertools.repeat(min_step,len(self.tuple_arguments)),
                                 itertools.repeat(penalty_val,len(self.tuple_arguments)),
                                 itertools.repeat(hour_limit,len(self.tuple_arguments))),
                                 total=len(self.tuple_arguments)))
             data_results=[x for x in results if isinstance(x, tuple)]
             dict_results=defaultdict(dict)
             for x in data_results:
                 dict_results[x[0][0]][x[0][1]]={}
                 dict_results[x[0][0]][x[0][1]]=x[1]
        execution_time=(time.time() - start)
             
        time_mins=round(execution_time/60,2)
        return time_mins,dict_results
        # return dict_results
    #pelt model takes dyanmic penalty
    def generate_models(self):
        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/space-time-pattern-mining/how-change-point-detection-works.html
        model1=self.thread_Process_model('BottomUp',1,'l2',10,penalty_val=50)
        model2=self.thread_Process_model('BottomUp',1,'rbf',100)
        model3=self.thread_Process_model('Kernal',1,'linear',10)
        model4=self.thread_Process_model('Window',1,'rbf',100)
        model5=self.thread_Process_model('Window',1,'l2',10)
        model6=self.thread_Process_model('Window',0.65,'rbf',100)
        model7=self.thread_Process_model('Window',1,'rbf',100,penalty_val=100)
        
        list_models=[model1,model2,model3,model4,model5,model6,model7]
        save_data(list_models,'Data/Models/list_models')
        return list_models

def main():
    one_Model()
def load():
    list_models=load_data('Data/Models/list_models')
    
    
    return list_models

if __name__=='__main__':
    main()

