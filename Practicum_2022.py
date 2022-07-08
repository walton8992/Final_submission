
# -*- coding: utf-8 -*-
"""
Class to generate CPDE array 

"""
from  utilities import save_data,change_working_dir,load_data
change_working_dir(r'C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final')
import ruptures as rpt
import numpy as np
from tqdm import tqdm
from ensemble_methods.aggregations import SCALING_AGGREGATION
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


class CPDE(object):
    
    def __init__(self,model,pen,dict_sites_melt,lookback_duration=False):
        self.model=model
        self.pen=pen
        if lookback_duration:
            self.dict_sites_melt=self._twentyfour_hours(dict_sites_melt)
        else:
            self.dict_sites_melt=dict_sites_melt

    def multiprocess(self,data):
        with ThreadPoolExecutor(max_workers = 4) as executor:
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
                try :
                    if type(scaling_agg) is list:
                        for scale in scaling_agg:
                            data=SCALING_AGGREGATION[scale] 
                            algo=self.get_algo(data)
                            try:
    
                                table_ensemble_window[scale] = self.fit_model(algo, y)
                            except:
                                table_ensemble_window[scale]=None
                except TypeError:
                    print("Scaling agg needs to be a list")
              
                return site,table_ensemble_window


    def get_algo(self,scale_aggregation):
        if self.model == 'window':
             algo = rpt.WindowEnsemble(
             width=10,
             models=LIST_COSTS,
             params=PARAMS, 
             scale_aggregation=scale_aggregation
            )
        elif self.model=='binseg':
             algo = rpt.BinsegEnsemble(
             min_size=5,
             models=LIST_COSTS,
             params=PARAMS, 
             scale_aggregation=scale_aggregation,
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
        
    def run(self,model):
       '''
        Parameters
        ----------
        model : algo from ensemble
        
            DESCRIPTION.

        Returns
        -------
        cpde : TYPE
            DESCRIPTION.
        cpde_combined : TYPE
            DESCRIPTION.
        '''
       variables = ['BElarge','BEsmall','EFlarge','EFsmall']

       tuple_arguments=[(x,y,model,['Min_Raw']) for x in self.dict_sites_melt.keys() for y in variables]
       
       with process.ProcessPoolExecutor(max_workers=3) as multiprocessing_executor:
                   chunk= [tuple_arguments[x:x+10] for x in range(0, len(tuple_arguments), 10)]
                   print("mapping ...")
                   r=multiprocessing_executor.map(model.multiprocess,chunk)
       final= [r for r in r]
       f2= [x for xs in final for x in xs if x is not None]
       cpde=self.dict_combine_cpde(f2)
       cpde_combined=self.dict_combine_cpde(f2,combine=True)

       return cpde,cpde_combined

def main(save=False):

    dict_sites_melt=load_data('Data/site_data_melted')
    binseg=CPDE('binseg',50,dict_sites_melt,False)
    window=CPDE('window',50,dict_sites_melt,False)
    binseg,binseg_flat=binseg.run(binseg)
    window,window_flat=window.run(window)
    # save_data(binseg, 'practicum_2022/Results/binseg_full')
    # save_data(binseg_flat, 'practicum_2022/Results/binseg_flat')

    # save_data(binseg, 'practicum_2022/Results/binseg_full_24')
    # save_data(binseg_flat, 'practicum_2022/Results/binseg_flat_24')
    
    # save_data(window, 'practicum_2022/Results/window_full_24')
    # save_data(window_flat, 'practicum_2022/Results/window_flat_24')
def load():
      
    binseg,binseg_flat=load_data('practicum_2022/Results/binseg_full'),load_data('practicum_2022/Results/binseg_flat')
    
    window,window_flat=load_data('practicum_2022/Results/window_full'),load_data('practicum_2022/Results/window_flat')
    
    return binseg,binseg_flat,window,window_flat

if __name__=='__main__':
    main()

    

if __name__!='__main__':
    print('loading..')
    load()
