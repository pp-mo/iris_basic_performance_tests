#!/bin/bash

#
# How to run standard performance tests for 3 Iris versions
# (as-is, rather specific to itpp ion eld238)
#

source activate dask_speedchecks
RESULTS_REPO=$(pwd)
IRIS_REPO=~/git/iris/iris_main

mkdir -p results/daskopts_latest
rm -f results/daskopts_latest/*

cd $IRIS_REPO

if [ "$(git branch | grep v2_latest_WITH_daskopts)" != "" ]; then
  echo "BRANCH EXISTS : v2_latest_WITH_daskopts"
else
  echo "MAKING BRANCH : v2_latest_WITH_daskopts @ 648727710"
  git branch v2_latest_WITH_daskopts 648727710
fi
if [ "$(git branch | grep v2_latest_WITHOUT_daskopts)" != "" ]; then
  echo "BRANCH EXISTS : v2_latest_WITHOUT_daskopts @ d0abb15f4"
else
  echo "MAKING BRANCH : v2_latest_WITHOUT_daskopts"
  git branch v2_latest_WITHOUT_daskopts d0abb15f4
fi

cd $IRIS_REPO
git checkout v2_latest_WITH_daskopts
. ../rebuild.sh
cd $RESULTS_REPO
python standard_performance_tests.py 2>&1 | tee results/daskopts_latest/performance_test_outputs_WITH_daskdefaults_x1.txt
python standard_performance_tests.py 2>&1 | tee results/daskopts_latest/performance_test_outputs_WITH_daskdefaults_x2.txt

cd $IRIS_REPO
git checkout v2_latest_WITHOUT_daskopts
. ../rebuild.sh
cd $RESULTS_REPO
python standard_performance_tests.py 2>&1 | tee results/daskopts_latest/performance_test_outputs_WITHOUT_daskdefaults_x1.txt
python standard_performance_tests.py 2>&1 | tee results/daskopts_latest/performance_test_outputs_WITHOUT_daskdefaults_x2.txt

cd $IRIS_REPO
git checkout latest
if [ "$(git branch | grep v2_latest_WITH_daskopts)" != "" ]; then
  echo "DELETING BRANCH : v2_latest_WITH_daskopts"
  git branch -D v2_latest_WITH_daskopts
fi
if [ "$(git branch | grep v2_latest_WITHOUT_daskopts)" != "" ]; then
  echo "DELETING BRANCH : v2_latest_WITHOUT_daskopts"
  git branch -D v2_latest_WITHOUT_daskopts
fi
