# -*- coding: utf-8 -*-
"""
Class to generate CPDE for input list of dictionaries, and variables - with CPDE

"""
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


class changePoint:
    """Class to generate dictionary of CPDE."""

    def __init__(
        self,
        model,
        pen,
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
            try:
                if type(scaling_agg) is list:
                    for scale in scaling_agg:
                        data = SCALING_AGGREGATION[scale]
                        algo = self.get_algo(data)
                        # try:

                        table_ensemble_window[scale] = self.fit_model(algo, y)
                        # except:
                        # table_ensemble_window[scale] = None
            except TypeError:
                print("Scaling agg needs to be a list")

            return site, table_ensemble_window

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

    def _multithreading(self, data):
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
            r = multiprocessing_executor.map(self._multithreading, chunk)
        final = [r for r in r]
        f2 = [x for xs in final for x in xs if x is not None]
        return f2


if __name__ == "__main__":

    dict_sites_melt = load_data("Data/site_data_melted")
    dict_sites_melt = dict(itertools.islice(dict_sites_melt.items(), 2))

    binseg = changePoint(
        model="binseg",
        pen=50,
        dict_sites_melt=dict_sites_melt,
        cost_function=["Min_Raw", "Sum_Raw", "Sum_MinMax", "Min_MinAbs"],
    )
    t1 = binseg.multiprocessing_method()
