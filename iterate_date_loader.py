# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 09:44:04 2022

@author: Alex
"""
from utilities import load_data, change_working_dir
import collections
import itertools
import CPDE_ensemble
from ensemble_methods.aggregations import SCALING_AGGREGATION


def split_dict(main_dict, split_number):
    """Split dict into manageable parts.
    params
    main_dcit - main melted dict of data.
    """
    key_list = list(main_dict.keys())
    # number in each dict
    splits = int(round((len(key_list) / (split_number)), 0))
    dict_split = []
    for i in range(split_number + 1):

        temp_dict = dict(
            (k, main_dict[k]) for k in key_list[i * splits : splits * (i + 1)]
        )
        if temp_dict.items():

            dict_split.append(temp_dict)

    # main_dict_final = dict(
    #     (k, main_dict[k]) for k in key_list[splits * (split_number - 1) :]
    # )
    # if main_dict_final.items():
    #     dict_split.append(main_dict_final)git
    com_dict = dict(itertools.chain(*(d.items() for d in dict_split)))

    assert len(com_dict.keys()) == len(main_dict), "Error in splitting dicts"

    FUNCTION_DICT = dict(
        ("dict_" + str(r), d) for r, d in enumerate(dict_split)
    )

    return FUNCTION_DICT


change_working_dir(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final"
)
dict_sites_melt_main = load_data("Data/site_data_melted")
# HINT split into smaller dicts for processing

dict_sites_melt_main = collections.OrderedDict(
    sorted(dict_sites_melt_main.items())
)
FUNCTION_DICT = split_dict(dict_sites_melt_main, 363)
#%%
for i in FUNCTION_DICT:
    CPDE_ensemble.main(f"{i}", FUNCTION_DICT)
