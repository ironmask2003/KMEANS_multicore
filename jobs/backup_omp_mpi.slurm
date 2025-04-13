#!/bin/bash
#SBATCH --job-name=kmeans_omp_mpi             # Job name
#SBATCH --output=jobs/logs_omp_mpi/out.%N     # Standard output log (%N = node name)
#SBATCH --error=jobs/logs_omp_mpi/err.%N      # Standard error log
#SBATCH --time=01:00:00                       # Max runtime (adjust as needed)
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=8

# Run the job using MPI
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export OMPI_MCA_btl_tcp_if_include=ibp129s0

srun --mpi=pmix ./KMEANS_omp_mpi test_files/input100D2.inp 40 100 1 0.0001 output_files/omp_mpi/output100D2.txt comp_time/omp_mpi/comp_time100D2.csv ${SLURM_CPUS_PER_TASK}
