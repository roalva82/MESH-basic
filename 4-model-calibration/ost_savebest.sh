#!/bin/bash

set -e

echo "saving input files for the best solution found ..."

if [ ! -e best ] ; then
    mkdir best
fi

cp model/MESH_parameters_CLASS.ini  best/MESH_parameters_CLASS.ini
cp model/results/Metric.csv best/Metric.csv 

exit 0

