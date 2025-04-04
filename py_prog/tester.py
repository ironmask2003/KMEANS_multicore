import unittest
import os
import subprocess

from run import main
from gen_plots import gen_plot


# Function used to add AvgTime to csv file
def addAvgTime(test_type, avgTimes):
    # Check if the path not exist
    if not os.path.exists(f"./test_csv/slurm/{test_type}_slurm.csv"):
        os.makedirs("./test_csv/slurm", exist_ok=True)
        # Create the file and write the header
        open(f"./test_csv/slurm/{test_type}_slurm.csv", "w").close()
        subprocess.run(
            [
                f"echo AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2 >> ./test_csv/slurm/{test_type}_slurm.csv"
            ],
            shell=True,
        )

    subprocess.run(
        [
            f"echo {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]} >> ./test_csv/slurm/{test_type}_slurm.csv"
        ],
        shell=True,
    )


def addAvgTime_omp_mpi(test_type, avgTimes, pcs, thread):
    # Check if the path not exist
    if not os.path.exists(f"./test_csv/slurm/{test_type}_{pcs}_slurm.csv"):
        os.makedirs("./test_csv/slurm", exist_ok=True)
        # Create the file and write the header
        open(f"./test_csv/slurm/{test_type}_{pcs}_slurm.csv", "w").close()
        subprocess.run(
            [
                f"echo Number of Process, Number of Thread, AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2 >> ./test_csv/slurm/{test_type}_{pcs}_slurm.csv"
            ],
            shell=True,
        )

    subprocess.run(
        [
            f"echo {pcs} {thread} {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]} >> ./test_csv/slurm/{test_type}_{pcs}_slurm.csv"
        ],
        shell=True,
    )


class MyTest(unittest.TestCase):
    def doTest(self, vers: str, test: str, pcs: int, thread: int):
        self.assertEqual(main(vers, test, pcs, thread), True)

    def run_omp_mpi(self, dimensions: list[str], vers: str):
        processes = [2, 4, 8]
        threads = [1, 2, 4, 8, 16, 32]

        for pcs, thread in [(p, t) for p in processes for t in threads]:
            print(f"Test with {pcs} process and {thread} thread")
            print("-----------------------------------------")
            avgTimes = []
            for dim in dimensions:
                # Remove comp_time files if exist
                if os.path.exists(f"./comp_time/{vers}/comp_time{dim}.csv"):
                    os.remove(f"./comp_time/{vers}/comp_time{dim}.csv")

                # Create comp_time files
                open(f"./comp_time/{vers}/comp_time{dim}.csv", "w").close()

                print(f"Start testing with {dim}")
                print("-----------------------------------------")
                for _ in range(25):
                    self.doTest(vers, dim, pcs, thread)

                times = []

                # Open comp_time file and read all lines
                with open(f"./comp_time/{vers}/comp_time{dim}.csv", "r") as f:
                    times = f.readlines()

                # Convert all element in the array to float
                times = [float(time) for time in times]

                # AvgTime
                avgTime = sum(times) / len(times)
                avgTimes.append(avgTime)

            addAvgTime_omp_mpi(vers, avgTimes, pcs, thread)
            print("-----------------------------------------")

    def main_test(self, dimensions: list[str], vers: str):
        # Check the version of the program to run
        if vers == "omp_mpi":
            self.run_omp_mpi(dimensions, vers)
            return
        # Array of avgTime for each test
        avgTimes = []

        # iterate over all test file
        for dim in dimensions:
            # Remove comp_time files if exist
            if os.path.exists(f"./comp_time/{vers}/comp_time{dim}.csv"):
                os.remove(f"./comp_time/{vers}/comp_time{dim}.csv")

            # Create comp_time files
            open(f"./comp_time/{vers}/comp_time{dim}.csv", "w").close()

            print(f"Start testing with {dim}")
            print("-----------------------------------------")
            for _ in range(25):
                self.doTest(vers, dim, 0, 0)
                print("Test done successfully")
                print("-----------------------------------------")

            times = []

            # Open comp_time file and read all lines
            with open(f"./comp_time/{vers}/comp_time{dim}.csv", "r") as f:
                times = f.readlines()

            # Convert all element in the array to float
            times = [float(time) for time in times]

            # AvgTime
            avgTime = sum(times) / len(times)
            avgTimes.append(avgTime)

        addAvgTime(vers, avgTimes)
        print("-----------------------------------------")

    def test(self):
        dimensions = ["2D2", "10D", "20D", "2D", "100D", "100D2"]

        print("Running CUDA test")
        print("-----------------------------------------")
        subprocess.run(["make", "KMEANS_cuda"])
        self.main_test(dimensions, "cuda")

        print("Running OMP_MPI test")
        print("-----------------------------------------")
        subprocess.run(["make", "KMEANS_omp_mpi"])
        self.main_test(dimensions, "omp_mpi")

        subprocess.run(["make", "clean"])

        print("Generating plots")
        print("-----------------------------------------")
        gen_plot()


if __name__ == "__main__":
    unittest.main()
