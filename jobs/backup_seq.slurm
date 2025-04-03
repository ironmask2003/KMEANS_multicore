#!/bin/bash
#SBATCH --job-name=kmeans_seq             # Job name
#SBATCH --output=jobs/logs_seq/out.%N     # Standard output log (%N = node name)
#SBATCH --error=jobs/logs_seq/err.%N      # Standard error log
#SBATCH --time=01:00:00                       # Max runtime (adjust as needed)
#SBATCH --nodes=1                           # Number of nodes
#SBATCH --ntasks=1                           # Total number of tasks (MPI processes)
#SBATCH --cpus-per-task=1                     # CPU cores per task
#SBATCH --partition=students                  # Adjust to the correct partition

./KMEANS_seq test_files/input100D.inp 40 100 1 0.0001 output_files/seq/output100D.txt comp_time/seq/comp_time100D.csv
