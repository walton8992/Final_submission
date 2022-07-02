
# -*- coding: utf-8 -*-
"""
Class

"""
import os

current_do=os.getcwd()
os.chdir(r'C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final')
DATA=r'C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\Data'
import ruptures as rpt
import numpy as np
import data_loading as data_load
from tqdm import tqdm
import bz2
import pickle
from ensemble_methods.aggregations import SCALING_AGGREGATION
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from concurrent.futures import process

# SCALING_AGGREGATION=SCALING_AGGREGATION.iloc[0]
SINGLE_COSTS = (
    {'name': 'ar_1', 'cost':'ar', 'params':{'order':1}},
    {'name': 'mahalanobis', 'cost':'mahalanobis', 'params':{}},
    {'name': 'l1', 'cost':'l1', 'params':{}},
    {'name': 'l2', 'cost':'l2', 'params':{}},
    {'name': 'rbf', 'cost': 'rbf', 'params': {}}
)
LIST_COSTS = [dict_cost["cost"] for dict_cost in SINGLE_COSTS]
PARAMS = {"ar": {'order':1}}

DESIRED_ORDER = ["Standart", "LowFP", "LowFN"]

def load_data_pbz(filename):
    dictionary = bz2.BZ2File(f'{filename}.pbz2', 'rb')
    dict_sites_melt = pickle.load(dictionary)
    return dict_sites_melt
dict_sites_melt=data_load.load_data(DATA+'\site_data_melted')


class CPDE(object):
    
    def __init__(self,model,pen,dict_sites_melt):
        self.model=model
        self.pen=pen
        # self.dict_sites_melt=dict_sites_melt

        self.dict_sites_melt=self._twentyfour_hours(dict_sites_melt)
    def multiprocess(self,data):
        with ThreadPoolExecutor(max_workers = 6) as executor:
            results = list(tqdm(executor.map(self.generate_cpde,data), total=len(data)))
        return results
    def generate_cpde(self,tuple_argument):
        
            site,var,model,scaling_agg=tuple_argument
            data_site=site
            y=np.array(self.dict_sites_melt[data_site][self.dict_sites_melt[data_site].variable == var].value).reshape(-1,1)
            if sum(y)[0]==0:
                pass
            else:
            
                table_ensemble_window = {}
                if  isinstance(scaling_agg,str):

                    data=SCALING_AGGREGATION[scaling_agg] 
                    algo=self.get_algo(data)
                    table_ensemble_window[data] = self.fit(algo,y)
                elif isinstance(scaling_agg,list):
                    for scale in scaling_agg:
                        data=SCALING_AGGREGATION[scale] 
                        algo=self.get_algo(data)
                        table_ensemble_window[scale] = self.fit_model(algo, y)
              
                return site,table_ensemble_window


    def get_algo(self,scale_aggregation):
        if self.model == 'window':
             algo = rpt.WindowEnsemble(
             width=10,
             models=LIST_COSTS,
             params=PARAMS, 
             scale_aggregation=scale_aggregation,
             jump=5)
        elif self.model=='binseg':
             algo = rpt.BinsegEnsemble(
             min_size=5,
             models=LIST_COSTS,
             params=PARAMS, 
             scale_aggregation=scale_aggregation,
             jump=5
         )
        return algo
    
    def fit_model(self,algo,y):
        algo.fit(y)
        my_bkps =algo.predict(pen=self.pen)
      
        return my_bkps
    def _twentyfour_hours(self,dictionary):
        
        
        for key, data in dictionary.items():
            # data_time = data[data]
            hour_zero=data.iloc[-1:].datetime.iloc[0]
            hour_24=hour_zero-timedelta(hours=24)
            data_test=data[data.datetime > hour_24].reset_index().drop(columns = 'index')
            dictionary[key]=data_test
        return dictionary
        
    def dict_combine_cpde(self,list_cp,combine=False):
        test={}
        for name,dic in list_cp:
            if name not in test.keys():
                test[name]=dic
            else:
                l=list(dic.items())
                for item in l:
                    test[name][item[0]]+=item[1]
                # test[name][item[0]]=list(set([name][item[0]]))
        #this is only if we want to combine all changepoints toether
        if combine:
            new_combined_dict={}
            for name,dic2 in test.items():
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
                    # else:
                    #     new_combined_dict[name]['all']=[]
            return new_combined_dict
        else:
            return test
        
    def run(self):
       
       variables = ['BElarge','BEsmall','EFlarge','EFsmall']

       tuple_arguments=[(x,y,'window',list(SCALING_AGGREGATION.keys())[:5]) for x in self.dict_sites_melt.keys() for y in variables]
       # processes = []

       # chunk= [tuple_arguments[x:x+10] for x in range(0, len(tuple_arguments), 10)][:5]

       # for i in chunk:
       #     p = multiprocessing.Process(target=self.multiprocess, args=(i))
       #     processes.append(p)
       
         
       # [x.start() for x in processes]
       
       with process.ProcessPoolExecutor(max_workers=6) as multiprocessing_executor:
                   chunk= [tuple_arguments[x:x+10] for x in range(0, len(tuple_arguments), 10)]
                   print("mapping ...")
                   r=multiprocessing_executor.map(test.multiprocess,chunk)
       final= [r for r in r]
       f2= [x for xs in final for x in xs if x is not None]
       cpde=self.dict_combine_cpde(f2)
       cpde_combined=self.dict_combine_cpde(f2,combine=True)

       return cpde,cpde_combined
def save_data(file,filename):
    with bz2.BZ2File(f'{filename}.pbz2', 'w') as f:
        pickle.dump(file, f)
def load_data_pbz(filename):
    dictionary = bz2.BZ2File(f'{filename}.pbz2', 'rb')
    dict_sites_melt = pickle.load(dictionary)
    return dict_sites_melt
start_time=time.time()


  
if __name__=='__main__':
    
    test=CPDE('binseg',100,dict_sites_melt)
    binseg,binseg_flat=test.run()
    save_data(binseg, 'Results/binseg_full')
    save_data(binseg_flat, 'Results/binseg_full_flat')

execution_time=(time.time() - start_time)
time_mins=round(execution_time,0)/60  


