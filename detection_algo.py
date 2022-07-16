# -*- coding: utf-8 -*-
"""
Live detection case

Use multiple thread and process to speed detection

"""
from utilities import load_data, change_working_dir
from CPDE_ensemble import changePoint
import itertools
import time
from Plotting import remove_unuseful_plots

change_working_dir(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022"
)
dict_sites_melt = load_data(r"Data\melted_dict_data\site_data_melted")
# HINT if need smaller dict
# small_dict = dict(itertools.islice(dict_sites_melt.items(), 5))

window = changePoint(
    model="window",
    pen=20,
    dict_sites_melt=dict_sites_melt,
    cost_function=list(["Min_MinAbs"]),
    lookback_duration=True,
)
if __name__ == "__main__":
    start_time = time.time()
    multiThread = window.multiprocessing_method()
    end_time = time.time()
    total_time = end_time - start_time
    main = window.dict_combine_cpde(multiThread)
    main = window.flatten_dict_all(main)
    main = remove_unuseful_plots(main)
