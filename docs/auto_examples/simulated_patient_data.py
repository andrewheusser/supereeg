# -*- coding: utf-8 -*-
"""
=============================
Simulate data
=============================

In this example, we load in a single subject example, remove electrodes that exceed
a kurtosis threshold (in place), load a model, and predict activity at all
model locations.

"""

# Code source: Andrew Heusser & Lucy Owen
# License: MIT

import superEEG as se
import scipy
import numpy as np
from superEEG._helpers.stats import r2z, z2r
from superEEG._helpers.bookkeeping import slice_list
from numpy import inf
from scipy.stats import zscore
import os
import pandas as pd
import pickle

# n_samples
n_samples = 1000

# load nifti to get locations
gray = se.load(os.path.dirname(os.path.abspath(__file__)) + '/../superEEG/data/gray_mask_20mm_brain.nii')

locs = gray.locs

# create 50 synthetic patient data with activity at every location
synth_dir = os.path.dirname(os.path.abspath(__file__)) + '/../superEEG/data/synthetic_data'
if not os.path.isdir(synth_dir):
    os.mkdir(synth_dir)

if not os.listdir(synth_dir):

    R = scipy.linalg.toeplitz(np.linspace(0,1,len(locs))[::-1])
    count = 0
    for p in range(50):

        rand_dist = np.random.multivariate_normal(np.zeros(len(locs)), np.eye(len(locs)), size=n_samples)
        bo = se.Brain(data=np.dot(rand_dist, scipy.linalg.cholesky(R)), locs=pd.DataFrame(locs, columns=['x', 'y', 'z']))
        bo.to_pickle(os.path.join(synth_dir, 'synthetic_'+ str(count).rjust(2, '0')))
        count += 1


model_data = []


for i in np.random.choice(range(50), 10, replace=False):

    p = np.random.choice(range(len(locs)), 20, replace=False)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/../superEEG/data/synthetic_data/synthetic_' +str(i).rjust(2, '0') + '.bo', 'rb') as handle:
        bo = pickle.load(handle)
        model_data.append(se.Brain(data=bo.data.iloc[:, p],locs= bo.locs.iloc[p]))

## create model with synthetic patient data, random sample 20 electrodes

R = scipy.linalg.toeplitz(np.linspace(0,1,len(locs))[::-1])
data = []
for i in range(50):

    p = np.random.choice(range(len(locs)), 20, replace=False)

    rand_dist = np.random.multivariate_normal(np.zeros(len(locs)), np.eye(len(locs)), size=n_samples)
    data.append(se.Brain(data=np.dot(rand_dist, scipy.linalg.cholesky(R))[:,p], locs=pd.DataFrame(locs[p,:], columns=['x', 'y', 'z'])))

    #bo.to_pickle(os.path.dirname(os.path.abspath(__file__)) + '/../superEEG/data/synthetic_' + str(i))
model = se.Model(data=data, locs=locs)

## create brain object to be reconstructed
## find indices
locs_inds = range(0,len(locs))
sub_inds = np.sort(np.random.choice(range(len(locs)), 20, replace=False))
unknown_inds = list(set(locs_inds)-set(sub_inds))

rand_dist = np.random.multivariate_normal(np.zeros(len(locs)), np.eye(len(locs)), size=n_samples)
full_data = np.dot(rand_dist, scipy.linalg.cholesky(R))
bo_sub = se.Brain(data=full_data[:, sub_inds], locs=pd.DataFrame(locs[sub_inds, :], columns=['x', 'y', 'z']))
bo_actual = se.Brain(data=full_data, locs=pd.DataFrame(locs, columns=['x', 'y', 'z']))

## need to figure out if we want to keep the activty used to predict - right now its added at the end, but that might not be the best
reconstructed = model.predict(bo_sub)

import seaborn as sb
sb.jointplot(reconstructed.data, bo_actual.data)