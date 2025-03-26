import subprocess


# Function used to check output file
def check_out(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                return False
    return True


# Functino used to run cuda version
def run(vers, test):
    subprocess.run(
        [
            f"./KMEANS_{vers} test_files/input{test}.inp 40 100 1 0.0001 output_files/{vers}/output{test}.txt comp_time/{vers}/comp_time{test}.csv"
        ],
        shell=True,
    )


def main(vers, test):
    run(vers, test)

    return check_out(
        f"output_files/seq/output{test}.txt",
        f"output_files/{vers}/output{test}.txt",
    )
