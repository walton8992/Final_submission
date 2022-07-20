# -*- coding: utf-8 -*-
"""
sktime claSP algorithm

@author: Alex
"""
from sktime.transformations.series.clasp import ClaSPTransformer
from sktime.annotation.clasp import find_dominant_window_sizes
from sktime.datasets import load_electric_devices_segmentation
import data_loading_v3 as data_load
import numpy as np
from sktime.annotation.clasp import (
    ClaSPSegmentation,
    find_dominant_window_sizes,
)
from sktime.annotation.plotting.utils import (
    plot_time_series_with_change_points,
    plot_time_series_with_profiles,
)

X, true_period_size, true_cps = load_electric_devices_segmentation()
dominant_period_size = find_dominant_window_sizes(X)
clasp = ClaSPTransformer(window_length=dominant_period_size).fit(X)
profile = clasp.transform(X)
ts, period_size, true_cps = load_electric_devices_segmentation()
from utilities import load_data

#%% Moore Ranch test
data = load_data(r"Data/melted_dict_data/site_data_melted")
area = "Sunset Crater"
X_moore = data[area][data[area]["variable"] == "BElarge"]["value"]
dominant_period_size = find_dominant_window_sizes(X_moore)

clasp = ClaSPSegmentation(
    period_length=dominant_period_size, n_cps=4, fmt="sparse"
)
found_cps = clasp.fit_predict(X_moore)
profiles = clasp.profiles
scores = clasp.scores
true_cps = np.array([105, 250])
print("The found change points are", found_cps.to_numpy())
