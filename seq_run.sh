#!/bin/bash

if [ "$1" == "100D" ]; then
  echo "Running test with input100D"
  make KMEANS_seq
  ./KMEANS_seq test_files/input100D.inp 40 100 1 0.0001 output_files/seq/output100D.txt comp_time/seq/comp_time100D.txt
elif [ "$1" == "100D2" ]; then
  echo "Running test with input100D2"
  make KMEANS_seq
  ./KMEANS_seq test_files/input100D2.inp 40 100 1 0.0001 output_files/seq/output100D2.txt comp_time/seq/comp_time100D2.txt
elif [ "$1" == "2D" ]; then
  echo "Runnin test with input2D"
  make KMEANS_seq
  ./KMEANS_seq test_files/input2D.inp 40 100 1 0.0001 output_files/seq/output2D.txt comp_time/seq/comp_time2D.txt
elif [ "$1" == "2D2" ]; then
  echo "Running test with input2D2"
  make KMEANS_seq
  ./KMEANS_seq test_files/input2D2.inp 40 100 1 0.0001 output_files/seq/output2D2.txt comp_time/seq/comp_time2D2.txt
elif [ "$1" == "10D" ]; then
  echo "Running test with input10D"
  make KMEANS_seq
  ./KMEANS_seq test_files/input10D.inp 40 100 1 0.0001 output_files/seq/output10D.txt comp_time/seq/comp_time10D.txt
elif [ "$1" == "20D" ]; then
  echo "Running test with input20D"
  make KMEANS_seq
  ./KMEANS_seq test_files/input20D.inp 40 100 1 0.0001 output_files/seq/output20D.txt comp_time/seq/comp_time20D.txt
else
  echo "All test running"
  make KMEANS_seq
  echo "2D2"
  ./KMEANS_seq test_files/input2D2.inp 40 100 1 0.0001 output_files/seq/output2D2.txt comp_time/seq/comp_time2D2.txt
  echo "10D"
  ./KMEANS_seq test_files/input10D.inp 40 100 1 0.0001 output_files/seq/output10D.txt comp_time/seq/comp_time10D.txt
  echo "20D"
  ./KMEANS_seq test_files/input20D.inp 40 100 1 0.0001 output_files/seq/output20D.txt comp_time/seq/comp_time20D.txt
  echo "2D"
  ./KMEANS_seq test_files/input2D.inp 40 100 1 0.0001 output_files/seq/output2D.txt comp_time/seq/comp_time2D.txt
  echo "100D"
  ./KMEANS_seq test_files/input100D.inp 40 100 1 0.0001 output_files/seq/output100D.txt comp_time/seq/comp_time100D.txt
  echo "100D2"
  ./KMEANS_seq test_files/input100D2.inp 40 100 1 0.0001 output_files/seq/output100D2.txt comp_time/seq/comp_time100D2.txt
fi

make clean
