#!/bin/bash
#SBATCH --job-name=kmeans_omp_mpi             # Job name
#SBATCH --output=jobs/logs_omp_mpi/out.%N     # Standard output log (%N = node name)
#SBATCH --error=jobs/logs_omp_mpi/err.%N      # Standard error log
#SBATCH --time=01:00:00                       # Max runtime (adjust as needed)
#SBATCH --nodes=1                           # Number of nodes
#SBATCH --ntasks=8                           # Total number of tasks (MPI processes)
#SBATCH --cpus-per-task=1                     # CPU cores per task
#SBATCH --partition=students                  # Adjust to the correct partition

# Run the job using MPI
mpirun -n 8 ./KMEANS_omp_mpi test_files/input100D.inp 40 100 1 0.0001 output_files/omp_mpi/output100D.txt comp_time/omp_mpi/comp_time100D.csv 16
