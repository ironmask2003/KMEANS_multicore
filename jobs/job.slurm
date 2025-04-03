#!/bin/bash
#SBATCH --job-name=kmeans_omp_mpi        # Job name
#SBATCH --output=jobs/logs_omp_mpi/out.%N   # Standard output log
#SBATCH --error=jobs/logs_omp_mpi/err.%N    # Standard error log
#SBATCH --time=01:00:00               # Max time (adjust as needed)
#SBATCH --partition=students              # Use the GPU partition (adjust if necessary)
#SBATCH --nodes=1                           # Number of nodes
#SBATCH --ntasks=8                           # Total number of tasks (MPI processes)
#SBATCH --cpus-per-task=1             # Number of CPU cores per task


mpirun -n 8 ./KMEANS_omp_mpi test_files/input100D2.inp 40 100 1 0.0001 output_files/omp_mpi/output100D2.txt comp_time/omp_mpi/comp_time100D2.csv 32
    