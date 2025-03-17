import os


# Function used to check if two files have the same content
def check_out(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                return False
    return True


# Function to set the job file of the MPI+OMP version
def set_mpi_omp_job_file(vers, test, num_process, num_thread):
    # Check if logs directory exists
    if not os.path.exists(f"jobs/logs_{vers}/"):
        os.mkdir(f"jobs/logs_{vers}/")

    with open(f"jobs/job_{vers}.sub", "w") as f:
        f.write("universe = parallel\n\n")
        f.write("executable = jobs/openmpiscript.sh\n\n")
        f.write(
            f"arguments = ./KMEANS_{vers} input{test}.inp 40 100 1 0.0001 output{test}.txt comp_time{test}.csv {num_thread}\n\n"
        )
        f.write("should_transfer_files = YES\n\n")
        f.write(
            f"transfer_input_files = KMEANS_{vers}, test_files/input{test}.inp \n\n"
        )
        f.write(f"output = jobs/logs_{vers}/out.$(NODE)\n\n")
        f.write(f"error = jobs/logs_{vers}/err.$(NODE)\n\n")
        f.write(f"log = jobs/logs_{vers}/log\n\n")
        f.write(f"machine_count = {num_process}\n\n")
        f.write("request_cpus = 32\n\n")
        f.write("getenv = True\n\n")
        f.write("queue\n")


# Function used to set the job file of the CUDA version
def set_cuda_job_file(vers, test):
    # Check if logs directory exists
    if not os.path.exists(f"jobs/logs_{vers}/"):
        os.mkdir(f"jobs/logs_{vers}/")

    with open(f"jobs/job_{vers}.sub", "w") as f:
        f.write("universe = vanilla\n\n")
        f.write("executable = ./KMEANS_cuda\n\n")
        f.write(
            f"arguments = test_files/input{test}.inp 40 100 1 0.0001 output_files/{vers}/output{test}.txt comp_time/{vers}/comp_time{test}.csv\n\n"
        )
        f.write(f"log = jobs/logs_{vers}/{vers}_job.log\n\n")
        f.write(f"output = jobs/logs_{vers}/{vers}_job.out\n\n")
        f.write(f"error = jobs/logs_{vers}/{vers}_job.err\n\n")
        f.write("request_gpus = 1\n\n")
        f.write("getenv = True\n\n")
        f.write("queue\n")

# Set job file for sequential test
def set_seq_job_file(vers, test):
    if not os.path.exists(f"jobs/logs_{vers}/"):
        os.mkdir(f"jobs/logs_{vers}/")

    with open(f"./jobs/job_{vers}.sub", "w") as f:
        f.write("universe = vanilla\n\n")
        f.write("executable = ./KMEANS_seq\n\n")
        f.write(f"arguments = test_files/input{test}.inp 40 100 1 0.0001 output_files/{vers}/output{test}.txt comp_time/{vers}/comp_time{test}.csv\n\n")
        f.write(f"log = jobs/logs_{vers}/{vers}_job.log\n\n")
        f.write(f"output = jobs/logs_{vers}/{vers}_job.out\n\n")
        f.write(f"error = jobs/logs_{vers}/{vers}_job.err\n\n")
        f.write("request_cpus = 1\n\n")
        f.write("getenv = True\n\n")
        f.write("queue\n")

# After setting the job file, commit the job and wait the execution of the job
def exec_job(job_file, vers):
    import subprocess

    subprocess.run(["condor_submit", f"{job_file}"])
    print("Waiting for test")
    if vers == "omp_mpi":
        subprocess.run(["condor_wait", f"jobs/logs_{vers}/log"])
        return
    else:
        subprocess.run(["condor_wait", f"jobs/logs_{vers}/{vers}_job.log"])
    return


# Function to run the test
def run_test(vers, test, num_process, num_thread):
    if vers == "omp_mpi":
        set_mpi_omp_job_file(vers, test, num_process, num_thread)
        job_file = f"jobs/job_{vers}.sub"
        exec_job(job_file, vers)
        return check_out(
            f"output{test}.txt",
            f"output_files/seq/output{test}.txt"
        )
    elif vers == "cuda":
        set_cuda_job_file(vers, test)
        job_file = f"jobs/job_{vers}.sub"
        exec_job(job_file, vers)
    else:
        set_seq_job_file(vers, test)
        job_file = f"jobs/job_{vers}.sub"
        exec_job(job_file, vers)

    # Check if the output files between sequential and MPI+OMP are the same
    return check_out(
        f"output_files/seq/output{test}.txt",
        f"output_files/{vers}/output{test}.txt",
    )
