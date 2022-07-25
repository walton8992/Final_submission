# -*- coding: utf-8 -*-
"""
Live detection case - to use one/many detected aggreagted cost function.

Use multiple thread and process to speed detection

"""
from utilities import load_data, change_working_dir, plot_change_points_pyplot
from CPDE_ensemble import changePoint
import itertools
import time
import collections


def remove_unuseful_plots(dictionary: dict):
    """Want to remove those with just line at the end of the plot."""
    new_dict = collections.defaultdict(dict)
    plot_dict = dictionary
    for key, item in plot_dict.items():
        if len(list(item.values())[0]) == 1:
            pass
        else:
            new_dict[key] = item
    return new_dict


dict_sites_melt = load_data("site_data_melted")
# HINT if need smaller dict
small_dict = dict(itertools.islice(dict_sites_melt.items(), 5))

window = changePoint(
    model="pelt",
    pen=30,
    dict_sites_melt=small_dict,
    cost_function=list(["Min_MinAbs"]),
    lookback_duration=False,
)
if __name__ == "__main__":
    start_time = time.time()
    multiThread = window.multiprocessing_method()
    end_time = time.time()
    total_time = end_time - start_time
    main = window.dict_combine_cpde(multiThread)
    main = window.flatten_dict_all(main)
    main = remove_unuseful_plots(main)
