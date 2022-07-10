# -*- coding: utf-8 -*-
"""Class to generate CPDE array."""
from utilities import change_working_dir, load_data, save_data
import ruptures as rpt
import numpy as np
from tqdm import tqdm
from ensemble_methods.aggregations import SCALING_AGGREGATION
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from concurrent.futures import process
import itertools

change_working_dir(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final"
)
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


class CPDE(object):
    def __init__(self, model, pen, dict_sites_melt, lookback_duration=False):
        self.model = model
        self.pen = pen
        if lookback_duration:
            self.dict_sites_melt = self._twentyfour_hours(dict_sites_melt)
        else:
            self.dict_sites_melt = dict_sites_melt

    def multiprocess(self, data):
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.generate_cpde, data))
        return results

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
            try:
                if type(scaling_agg) is list:
                    for scale in scaling_agg:
                        data = SCALING_AGGREGATION[scale]
                        algo = self.get_algo(data)
                        try:

                            table_ensemble_window[scale] = self.fit_model(
                                algo, y
                            )
                        except:
                            table_ensemble_window[scale] = None
            except TypeError:
                print("Scaling agg needs to be a list")

            return site, table_ensemble_window

    def get_algo(self, scale_aggregation):
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
        return algo

    def fit_model(self, algo, y):
        algo.fit(y)
        my_bkps = algo.predict(pen=self.pen)

        return my_bkps

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

    def dict_combine_cpde(self, list_cp, combine=False):
        """Get all."""
        test = {}
        for name, dic in list_cp:
            if name not in test.keys():
                test[name] = dic
            else:
                list_dic = list(dic.items())
                for item in list_dic:
                    test[name][item[0]] += item[1]
                    save_data(
                        test,
                        "practicum_2022/Results/"
                        "binseg_full_5_cost_functions",
                    )
        # this is only if we want to combine all changepoints toether
        if combine:
            new_combined_dict = {}
            for name, dic2 in test.items():
                new_combined_dict[name] = {}
                new_combined_dict[name]["all"] = []
                for cost, list_cp in dic2.items():
                    list_cp_unique = list(set(list_cp))

                    # if len(list_cp_unique)>1:
                    if name not in new_combined_dict:
                        new_combined_dict[name]["all"] = list_cp_unique
                    else:
                        new_combined_dict[name]["all"] += list_cp_unique
                new_combined_dict[name]["all"] = list(
                    set(new_combined_dict[name]["all"])
                )
                # else:
                #     new_combined_dict[name]['all']=[]
            return new_combined_dict
        else:
            return test

    def run(self, model, cost_function: list):
        """
        Parameters.

        ----------
        model : algo from ensemble
        Returns
        -------
        cpde : TYPE
            DESCRIPTION.
        cpde_combined : TYPE
            DESCRIPTION
        """
        print("run")
        variables = ["BElarge", "BEsmall", "EFlarge", "EFsmall"]

        tuple_arguments = [
            (x, y, model, cost_function)
            for x in self.dict_sites_melt.keys()
            for y in variables
        ]
        tuple_arguments = tuple_arguments[:1]

        with process.ProcessPoolExecutor(
            max_workers=6
        ) as multiprocessing_executor:
            chunk = [
                tuple_arguments[x : x + 10]
                for x in range(0, len(tuple_arguments), 10)
            ]
            print("mapping ...")
            r = multiprocessing_executor.map(model.multiprocess, chunk)
        final = [r for r in r]
        f2 = [x for xs in final for x in xs if x is not None]
        # cpde = self.dict_combine_cpde(f2)
        # cpde_combined = self.dict_combine_cpde(f2, combine=True)

        return f2  # cpde_combined


# %%
def main():
    """Run CPDE class."""
    # HINT - Load data, penalty here is seconds class input
    dict_sites_melt = load_data("Data/site_data_melted")
    binseg = CPDE("binseg", 50, dict_sites_melt, False)
    variables = ["BElarge", "BEsmall", "EFlarge", "EFsmall"]

    tuple_arguments = [
        (x, y, binseg, ["Min_Raw"])
        for x in dict_sites_melt.keys()
        for y in variables
    ]
    tuple_arguments = tuple_arguments[0]
    # %%
    t1 = binseg.generate_cpde(tuple_arguments)
    cpde = binseg.dict_combine_cpde([t1])
    # %%
    # window = CPDE("window", 50, dict_sites_melt, False)

    # HINT
    # Generate Binseg for all 5 of the below, both flat and combined
    list_cost_functions = ["Min_Raw", "Sum_Raw", "Sum_MinMax", "Min_MinAbs"]
    binseg, binseg_flat = binseg.run(binseg, list_cost_functions)
    return binseg, binseg_flat
    # save_data(binseg, "practicum_2022/Results/binseg_full_4_cost_functions")

    # save_data(
    #     binseg_flat, "practicum_2022/Results/binseg_flat_4_cost_functions"
    # )

    # t=load_data("practicum_2022/Results/binseg_flat_Min_Znorm")

    # window, window_flat = window.run(
    # window,
    # [
    # "Min_Raw",
    # "Sum_Raw",
    # "Sum_MinMax",
    # "Min_MinAbs",
    # "Min_Znorm",
    # "Min_Rank",
    # ],
    # )

    # save_data(window,
    # "practicum_2022/Results/window_full_24_5_cost_functions")

    # save_data(
    #     window_flat, "practicum_2022/Results/window_flat_24_5_cost_functions"
    # )


def load_flat():
    """
    Load iteration of data from CPDE class.

    Returns
    -------
    binseg : Dict
    binseg_flat : Dict
    window : Dict
    window_flat : Dict
    """
    binseg, binseg_flat = load_data(
        "practicum_2022/Results/binseg_full"
    ), load_data("practicum_2022/Results/binseg_flat")

    window, window_flat = load_data(
        "practicum_2022/Results/window_full"
    ), load_data("practicum_2022/Results/window_flat")

    return binseg, binseg_flat, window, window_flat


if __name__ == "__main__":
    dict_sites_melt = load_data("Data/site_data_melted")
    binseg = CPDE("binseg", 50, dict_sites_melt, False)
    # variables = ["BElarge", "BEsmall", "EFlarge", "EFsmall"]
    list_cost_functions = ["Min_Raw", "Sum_Raw", "Sum_MinMax", "Min_MinAbs"]

    # tuple_arguments = [
    #     (x, y, binseg, list_cost_functions)
    #     for x in dict_sites_melt.keys()
    #     for y in variables
    # ]
    # tuple_arguments = tuple_arguments[0]
    # %%
    t1 = binseg.run(binseg, list_cost_functions)
    # cpde = binseg.dict_combine_cpde([t1])


if __name__ != "__main__":
    print("loading..")

    load_flat()
