# -*- coding: utf-8 -*-
"""
Class to generate CPDE for input list of dictionaries, and variables - with CPDE

if run alone can give args to generate data

"""
from utilities import change_working_dir, load_data, save_data, timethis
import ruptures as rpt
import numpy as np
from tqdm import tqdm
from ensemble_methods.aggregations import SCALING_AGGREGATION
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from concurrent.futures import process
import itertools
import collections
import pandas as pd
import argparse
import multiprocessing

# SCALING_AGGREGATION=SCALING_AGGREGATION.iloc[0]
SINGLE_COSTS = (
    {"name": "ar_1", "cost": "ar", "params": {"order": 1}},
    {"name": "mahalanobis", "cost": "mahalanobis", "params": {}},
    {"name": "l1", "cost": "l1", "params": {}},
    {"name": "l2", "cost": "l2", "params": {}},
    {"name": "rbf", "cost": "rbf", "params": {}},
)
LIST_COSTS = [dict_cost["cost"] for dict_cost in SINGLE_COSTS]
PARAMS = {"ar": {"order": 1}}

DESIRED_ORDER = ["Standart", "LowFP", "LowFN"]


class changePoint:
    """Class to generate dictionary of CPDE."""

    def __init__(
        self,
        model: type(rpt),
        pen: int,
        cost_function: list,
        dict_sites_melt: dict,
        lookback_duration=False,
    ):
        """
        Initiate Class.

        Class that we can iterate.over each timeseries in provided dict.

        Parameters
        ----------
        model :

        pen :

        lookback_duration : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """
        self.dict_sites_melt = dict_sites_melt
        self.model = model
        self.pen = pen
        self.tuple_arguments = self._generate_tuple_argument(
            self.model, self.dict_sites_melt, cost_function
        )
        if lookback_duration:
            self.dict_sites_melt = self._twentyfour_hours(self.dict_sites_melt)
        else:
            self.dict_sites_melt = self.dict_sites_melt

    def fit_model(self, algo, y):
        """Fit model.

        Detect CPD.
        """
        algo.fit(y)
        my_bkps = algo.predict(pen=self.pen)

        return my_bkps

    def generate_cpde(self, tuple_argument):
        """Find changepoiunt detection points using lisdt of cost functions."""
        site, var, model, scaling_agg = tuple_argument
        data_site = site
        y = np.array(
            self.dict_sites_melt[data_site][
                self.dict_sites_melt[data_site].variable == var
            ].value
        ).reshape(-1, 1)
        if sum(y)[0] == 0:
            pass
        else:

            table_ensemble_window = {}
            table_ensemble_window[var] = {}
            try:
                if type(scaling_agg) is list:
                    for scale in scaling_agg:
                        data = SCALING_AGGREGATION[scale]
                        algo = self.get_algo(data)
                        try:

                            table_ensemble_window[var][scale] = self.fit_model(
                                algo, y
                            )
                        except:
                            table_ensemble_window[scale] = None
            except TypeError:
                print("Scaling agg needs to be a list")
            return site, table_ensemble_window

    def _twentyfour_hours(self, dictionary):

        for key, data in dictionary.items():
            # data_time = data[data]
            hour_zero = data.iloc[-1:].datetime.iloc[0]
            hour_24 = hour_zero - timedelta(hours=24)
            data_test = (
                data[data.datetime > hour_24]
                .reset_index()
                .drop(columns="index")
            )
            dictionary[key] = data_test
        return dictionary

    def get_algo(self, scale_aggregation):
        """Determine the algorithm to use.

        Parameters:
            -Scale_aggregation :
                list of string for each aggration/cost function.

        Returns.
            -algo : TYPE ruptuers model used.
        """
        if self.model == "window":
            algo = rpt.WindowEnsemble(
                width=10,
                models=LIST_COSTS,
                params=PARAMS,
                scale_aggregation=scale_aggregation,
            )
        elif self.model == "binseg":
            algo = rpt.BinsegEnsemble(
                min_size=5,
                models=LIST_COSTS,
                params=PARAMS,
                scale_aggregation=scale_aggregation,
            )
        elif self.model == "pelt":
            algo = rpt.Pelt(
                min_size=5,
                model="l2",
                params=None,
            )
        return algo

    def _generate_tuple_argument(
        self, model: str, dict_sites: dict, cost_function: list
    ):
        """Generate tuple arguemnt."""
        variables = ["BElarge", "BEsmall", "EFlarge", "EFsmall"]
        tuple_arguments = [
            (x, y, model, cost_function)
            for x in self.dict_sites_melt.keys()
            for y in variables
        ]
        return tuple_arguments

    def multithreading(self, data):
        """Multithreading model.

        To be used with parallel pricessing to speed up
        """
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.generate_cpde, data))
        return results

    def multiprocessing_method(self):
        """Run multiprocess."""
        with process.ProcessPoolExecutor(
            max_workers=6
        ) as multiprocessing_executor:
            chunk = [
                self.tuple_arguments[x : x + 10]
                for x in range(0, len(self.tuple_arguments), 10)
            ]
            print("mapping ...")
            r = multiprocessing_executor.map(self.multithreading, chunk)
        final = [r for r in r]
        f2 = [x for xs in final for x in xs if x is not None]
        return f2

    def dict_combine_cpde(self, list_cp, combine=False):
        """Get all from list of tuples to dict.

        This should return dict in format of each site,
        each variable and then each cpde detected for that variable

        Returns:
            -dict
        """
        test = {}
        for name, dic in list_cp:
            if name not in test.keys():
                test[name] = dic
            else:
                list_dic = list(dic.items())
                for item in list_dic:
                    # HINT item here is a tuple of
                    # variable and the cost function cPD detected

                    test[name][item[0]] = item[1]

        return test

    def flatten_dict_all(self, dictionary_results: dict):
        """Flatten dict one stage further.

        We want to be able to flatten to see,
        for each of the cost functions, what cpde we get
        and then compare each method with graphs.

        Args:
            -dict

        Returns:
                -dict
        """
        new_dict = {}
        for site, feature_var in dictionary_results.items():
            new_dict[site] = {}
            list_of_features = list(feature_var.keys())
            for feature in list_of_features:
                data = feature_var[feature]
                for cost, changepoint in data.items():
                    if cost not in new_dict[site]:

                        new_dict[site][cost] = changepoint
                    else:
                        new_dict[site][cost] = list(
                            set(changepoint + new_dict[site][cost])
                        )

        return new_dict


def split_dict(main_dict, split_number):
    """Split dict into manageable parts.
    params
    main_dcit - main melted dict of data.
    """
    key_list = list(main_dict.keys())
    # number in each dict
    splits = int(round((len(key_list) / (split_number)), 0)) + 1
    dict_split = []
    for i in range(split_number + 1):

        temp_dict = dict(
            (k, main_dict[k]) for k in key_list[i * splits : splits * (i + 1)]
        )
        if temp_dict.items():

            dict_split.append(temp_dict)

    com_dict = dict(itertools.chain(*(d.items() for d in dict_split)))

    assert len(com_dict.keys()) == len(main_dict), "Error in splitting dicts"

    FUNCTION_DICT = dict(
        ("dict_" + str(r), d) for r, d in enumerate(dict_split)
    )

    return FUNCTION_DICT


def main(dictionary, FUNCTION_DICT):

    dict_sites_melt_main = load_data(
        r"site_data_melted"
    )
    # HINT split into smaller dicts for processing

    dict_sites_melt_main = collections.OrderedDict(
        sorted(dict_sites_melt_main.items())
    )
    # FUNCTION_DICT = split_dict(dict_sites_melt_main, 100)
    dict_run_model = FUNCTION_DICT[dictionary]

    # print("test", args.dictionary)
    binseg = changePoint(
        model="window",
        pen=30,
        dict_sites_melt=dict_run_model,
        cost_function=list(list(SCALING_AGGREGATION.keys())),
    )
    # HINT drop and run mutliprcoess is smaller#
    t1 = binseg.multithreading(binseg.tuple_arguments)
    save_data(
        t1,
        "results/" "window" + dictionary,
    )
    print(f"Saving {dictionary}")


# %% Run main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dictionary", help="Dictionary of list", type=str
    )
    parser.add_argument("-s", "--splits", help="number of splits", type=int)

    args = parser.parse_args()
    main_dict = load_data("site_data_melted")
    FUNCTION_DICT = split_dict(main_dict, args.splits)
    main(args.dictionary, FUNCTION_DICT)
