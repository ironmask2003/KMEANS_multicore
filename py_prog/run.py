import subprocess
import re
import time


# Function used to check if two file are equal
def check_file(file1: str, file2: str) -> bool:
    with open(file1, "r") as f1, open(file2, "r") as f2:
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                return False
    return True


def format_file(vers: str, pcs: int, thread: int, test: str) -> str:
    return f"""#!/bin/bash
#SBATCH --job-name=kmeans_{vers}        # Job name
#SBATCH --output=jobs/logs_{vers}/out.%N   # Standard output log
#SBATCH --error=jobs/logs_{vers}/err.%N    # Standard error log
#SBATCH --time=01:00:00               # Max time (adjust as needed)
#SBATCH --partition=students              # Use the GPU partition (adjust if necessary)
{'#SBATCH --gres=gpu:1                  # Request 1 GPU' if vers=='cuda' else '#SBATCH --nodes=1                           # Number of nodes'}{f'\n#SBATCH --ntasks={1 if vers == 'seq' else 8}                           # Total number of tasks (MPI processes)' if vers!='cuda' else ''}
#SBATCH --cpus-per-task=1             # Number of CPU cores per task
{'#SBATCH --mem=4G                      # Memory per node (adjust as needed)' if vers=='cuda' else ''}

{
    f'./KMEANS_cuda test_files/input{test}.inp 40 100 1 0.0001 output_files/cuda/output{test}.txt comp_time/cuda/comp_time{test}.csv' if vers=='cuda' else 
    f'mpirun -n {pcs} ./KMEANS_omp_mpi test_files/input{test}.inp 40 100 1 0.0001 output_files/omp_mpi/output{test}.txt comp_time/omp_mpi/comp_time{test}.csv {thread}' if vers == 'omp_mpi' else
    f'./KMEANS_seq test_files/input{test}.inp 40 100 1 0.0001 output_files/seq/output{test}.txt comp_time/seq/comp_time{test}.csv'
}
    """


# Function to check if job is still running
def is_job_running(job_id):
    result = subprocess.run(["squeue", "-j", job_id], capture_output=True, text=True)
    return job_id in result.stdout  # If job_id is in output, job is still running


def wait_job():
    # Run job with sbatch command
    sbatch_output = subprocess.run(
        ["sbatch", "jobs/job.slurm"], capture_output=True, text=True
    )

    # Extract the job ID from the sbatch output
    match = re.search(r"Submitted batch job (\d+)", sbatch_output.stdout)
    if not match:
        print("Error: Could not extract Job ID from sbatch output.")
        exit(1)

    job_id = match.group(1)
    print(f"Submitted job {job_id}, waiting for completion...")

    # Wait for the job to complete
    while is_job_running(job_id):
        print(f"Job {job_id} is still running...")
        time.sleep(5)  # Check every 30 seconds

    print(f"Job {job_id} has completed!")


def run_seq(test: str):
    print("Running sequential test")

    # Set job file
    with open("jobs/job.slurm", "r+") as f:
        f.truncate(0)
        f.write(format_file("seq", 0, 0, test))

    wait_job()


def run_vers(vers: str, test: str, pcs: int, thread: int):
    print(f"Running {'CUDA' if vers=='cuda' else 'OMP + MPI'} test")

    # Set job file
    with open("jobs/job.slurm", "r+") as f:
        f.truncate(0)
        f.write(format_file(vers, pcs, thread, test))

    wait_job()


def main(vers: str, test: str, pcs: int, thread: int):
    # run_seq(test)
    run_vers(vers, test, pcs, thread)

    print("Check output files")
    return check_file(
        f"output_files/seq/output{test}.txt",
        f"output_files/{vers}/output{test}.txt",
    )


if __name__ == "__main__":
    main("omp_mpi", "100D2", 8, 32)
