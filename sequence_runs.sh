#!/bin/bash

source activate dask_speedchecks
IRIS_REPO=~/git/iris/iris_main

mkdir -p results/latest
rm -f results/latest/*

cd $IRIS_REPO
git checkout v_1x13x0
cd -
python standard_performance_tests.py 2>&1 | tee results/latest/performance_test_outputs_1v13_x1.txt
python standard_performance_tests.py 2>&1 | tee results/latest/performance_test_outputs_1v13_x2.txt

cd $IRIS_REPO
git checkout v_2.0a0
cd -
python standard_performance_tests.py 2>&1 | tee results/latest/performance_test_outputs_2v0a0_x1.txt
python standard_performance_tests.py 2>&1 | tee results/latest/performance_test_outputs_2v0a0_x2.txt

cd $IRIS_REPO
git checkout nc_simple_chunks
cd -
python standard_performance_tests.py 2>&1 | tee results/latest/performance_test_outputs_SMALLCHUNKS_x1.txt
python standard_performance_tests.py 2>&1 | tee results/latest/performance_test_outputs_SMALLCHUNKS_x2.txt


