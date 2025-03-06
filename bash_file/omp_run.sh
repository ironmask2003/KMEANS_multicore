#!/bin/bash

if [ "$1" == "100D" ]; then
  echo "Running test with input100D"
  make KMEANS_omp
  ./KMEANS_omp test_files/input100D.inp 40 100 1 0.0001 output_files/omp/output100D.txt comp_time/omp/comp_time100D.txt
elif [ "$1" == "100D2" ]; then
  echo "Running test with input100D2"
  make KMEANS_omp
  ./KMEANS_omp test_files/input100D2.inp 40 100 1 0.0001 output_files/omp/output100D2.txt comp_time/omp/comp_time100D2.txt
elif [ "$1" == "2D" ]; then
  echo "Runnin test with input2D"
  make KMEANS_omp
  ./KMEANS_omp test_files/input2D.inp 40 100 1 0.0001 output_files/omp/output2D.txt comp_time/omp/comp_time2D.txt
elif [ "$1" == "2D2" ]; then
  echo "Running test with input2D2"
  make KMEANS_omp
  ./KMEANS_omp test_files/input2D2.inp 40 100 1 0.0001 output_files/omp/output2D2.txt comp_time/omp/comp_time2D2.txt
elif [ "$1" == "10D" ]; then
  echo "Running test with input10D"
  make KMEANS_omp
  ./KMEANS_omp test_files/input10D.inp 40 100 1 0.0001 output_files/omp/output10D.txt comp_time/omp/comp_time10D.txt
elif [ "$1" == "20D" ]; then
  echo "Running test with input20D"
  make KMEANS_omp
  ./KMEANS_omp test_files/input20D.inp 40 100 1 0.0001 output_files/omp/output20D.txt comp_time/omp/comp_time20D.txt
fi

make clean
