#!/usr/bin/env python3
# PBS -l nodes=1:ppn=16
# PBS -l walltime=72:00:00
# PBS -N ala_rnd
# PBS -j oe

import os
import itertools
import pickle
from multiprocessing import Pool

import numpy

import qaccel
from qaccel.reference.alanine import ref_msm
from qaccel.adapt import Random
from qaccel.simulator import TMatSimulator
from qaccel.builder import MSMBuilder
from qaccel.convergence import Frobenius


os.chdir(os.environ.get("PBS_O_WORKDIR", "."))

# Define the search space
def get_params():
    spts = [2 ** i for i in range(4, 10)]
    tprs = [10 ** i for i in range(4)]
    for spt, tpr in itertools.product(spts, tprs):
        yield qaccel.Param(spt=spt, tpr=tpr)


# Define initial conditions
def initial(run):
    return numpy.random.randint(run.conv.true_n)

# Prepare the calculation
func, args = qaccel.get_map(
    param_gen=get_params(),
    ref_msm=ref_msm(),
    adapt=Random,
    simulator=TMatSimulator,
    builder=MSMBuilder,
    convergence=Frobenius,
    initial_func=initial
)

# Run the calculation
with Pool(16) as pool:
    results = pool.map(func, args)

# Save the results
with open("results.pickl", 'wb') as f:
    pickle.dump(results, f)
