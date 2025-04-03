#!/bin/bash
#SBATCH --job-name=kmeans_cuda        # Job name
#SBATCH --output=jobs/logs_cuda/cuda_job.out   # Standard output log
#SBATCH --error=jobs/logs_cuda/cuda_job.err    # Standard error log
#SBATCH --time=01:00:00               # Max time (adjust as needed)
#SBATCH --partition=students              # Use the GPU partition (adjust if necessary)
#SBATCH --gres=gpu:1                  # Request 1 GPU
#SBATCH --cpus-per-task=1             # Number of CPU cores per task
#SBATCH --mem=4G                      # Memory per node (adjust as needed)

# Load necessary environment variables
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Run the executable with arguments
./KMEANS_cuda test_files/input100D2.inp 40 100 1 0.0001 output_files/cuda/output100D2.txt comp_time/cuda/comp_time100D2.csv
