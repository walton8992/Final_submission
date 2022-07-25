# practicum_2022
Summer 2022 Commnet practicum for changepoint

The purpose of this practicum is to investigate different methods of detecting significant changepoints in a set of time series data. Some of this data is extremely noisy
The three main scripts are:
	CPDE_ensemble.py, detection_algo.py and autoencoder_tire.py

Utilities.py provides load and save functions. The iterate_data_loader.py will generate all agg.functions for specific method and penalty in CPDE_ensemble.py - used to test which method and agg.function is best.
Interactive_CPDE_py is used to plot those grahs generated from iterate_data.py

To Run.

Create conda environment from environment.yml file. This should install pre-requisites. Alternatively, use pip install -r requirements.txt - this should install all dependencies. (this was created in conda for the running of the below models)

The CPDE ensemble class is set up to allow the user to run a window, binseg or pelt algorithm, with a predetermined penalty if they wish. This then run the CPDE algorithm with an aggregated cost function. 
Running it as a main will generate all changepoints. The correct way to approach this is to run using detection_algo.py
You can then change the model, pen and the cost function to the chosen one to assess the impact. This is then outputting dictionaries that shows detected changepoints for the method, cost function and penalty set. 

Autoencoder.py

This is the TIRE model. most testing was done offline. Again, the function to reduce the dictionary to 24 hours is applied. it can be run without this. 
run the model as main.

The utilities folder is needed to load and test the data. This can be done another way as long as it is in a "melted dictionary" format. That is, for each site as the key, the item of the dictionary is a data frame of 4 columns:
	name(site), datatime, variable [EFsmall, EFlarge, BEsmall, BElarge
You should be then able to run the CPDE_ensemble method, or the autocoder_tire main.

When running CPDE detection MAKE SURE to download the ruptures files from folder. This includes the CPDE detection methodology - cannot obtain online from ruptures package. You download ruptures from yml file then copy ruptures from submission to environment


site_data_melted. pbz2 is the format needed when running the data. This is generated from the create_data.py from sql database. can be edited as needed.

You can change the hyperparameters of the autoencoder_tire.py This works by creating dissimilarity peaks. Then we analyse for changepoints using SciPy. This seems to be much better than standard changepoint.

All plots are put into submission folder.
