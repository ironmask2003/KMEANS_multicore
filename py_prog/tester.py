import unittest
import os
import subprocess

from run import main
from time_distribution import time_distribution


# Function used to add AvgTime to csv file
def addAvgTime(test_type, avgTimes):
    # Check if the path not exist
    if not os.path.exists(f"./test_csv/slurm/{test_type}_slurm.csv"):
        os.makedirs("./test_csv/slurm", exist_ok=True)
        # Create the file and write the header
        open(f"./test_csv/slurm/{test_type}_slurm.csv", "w").close()
        subprocess.run(
            [
                f"echo AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2, AvgTime100D_200K, AvgTime100D_400K, AvgTime100D_800K, AvgTime100D_1000K >> ./test_csv/slurm/{test_type}_slurm.csv"
            ],
            shell=True,
        )

    subprocess.run(
        [
            f"echo {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]}, {avgTimes[6]}, {avgTimes[7]}, {avgTimes[8]}, {avgTimes[9]} >> ./test_csv/slurm/{test_type}_slurm.csv"
        ],
        shell=True,
    )


def addAvgTimeCuda(test_type: str, avgTimes: list[float], t_block: int):
    # Check if the path not exist
    if not os.path.exists(f"./test_csv/slurm/{test_type}_slurm.csv"):
        os.makedirs("./test_csv/slurm", exist_ok=True)
        # Create the file and write the header
        open(f"./test_csv/slurm/{test_type}_slurm.csv", "w").close()
        subprocess.run(
            [
                f"echo Thread per blocco, AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2, AvgTime100D_200K, AvgTime100D_400K, AvgTime100D_800K, AvgTime100D_1000K >> ./test_csv/slurm/{test_type}_slurm.csv"
            ],
            shell=True,
        )

    subprocess.run(
        [
            f"echo {t_block}, {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]}, {avgTimes[6]}, {avgTimes[7]}, {avgTimes[8]}, {avgTimes[9]} >> ./test_csv/slurm/{test_type}_slurm.csv"
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
                f"echo Number of Process, Number of Thread, AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2, AvgTime100D_200K, AvgTime100D_400K, AvgTime100D_800K, AvgTime100D_1000K >> ./test_csv/slurm/{test_type}_{pcs}_slurm.csv"
            ],
            shell=True,
        )

    subprocess.run(
        [
            f"echo {pcs}, {thread}, {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]}, {avgTimes[6]}, {avgTimes[7]}, {avgTimes[8]}, {avgTimes[9]} >> ./test_csv/slurm/{test_type}_{pcs}_slurm.csv"
        ],
        shell=True,
    )


class MyTest(unittest.TestCase):
    def doTest(self, vers: str, test: str, pcs: int, thread: int):
        self.assertEqual(main(vers, test, pcs, thread), True)

    def run_tests(self, dim: str, vers: str, pcs: int, thread: int) -> float:
        # Remove comp_time files if exist
        if os.path.exists(f"./comp_time/{vers}/comp_time{dim}.csv"):
            os.remove(f"./comp_time/{vers}/comp_time{dim}.csv")

        # Create comp_time files
        open(f"./comp_time/{vers}/comp_time{dim}.csv", "w").close()

        print(f"Start testing with {dim}")
        print("-----------------------------------------")
        for _ in range(25):
            self.doTest(vers, dim, pcs, thread)
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
        return avgTime

    def run_cuda(self, dimensions: list[str], vers: str):
        t_blocks = [256, 512, 1024]

        for tb in t_blocks:
            print(f"Test with {tb} thread per block")
            print("-----------------------------------------")
            avgTimes = []
            for dim in dimensions:
                avgTimes.append(self.run_tests(dim, vers, 0, tb))

            addAvgTimeCuda(vers, avgTimes, tb)
            print("-----------------------------------------")

    def run_omp_mpi(self, dimensions: list[str], vers: str):
        processes = [2, 4, 8]
        threads = [1]

        for pcs, thread in [(p, t) for p in processes for t in threads]:
            print(f"Test with {pcs} process and {thread} thread")
            print("-----------------------------------------")
            avgTimes = []
            for dim in dimensions:
                # Test with 2D2 and 100D_1000K
                if dim != "2D2" and dim != "100D_1000K":
                    continue
                avgTimes.append(self.run_tests(dim, vers, pcs, thread))

            # Generate median and time distribution plot
            time_distribution(vers, pcs)

            # addAvgTime_omp_mpi(vers, avgTimes, pcs, thread)
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
            avgTimes.append(self.run_tests(dim, vers, 0, 0))

        addAvgTime(vers, avgTimes)
        print("-----------------------------------------")

    def test(self):
        dimensions = [
            "2D2",
            "10D",
            "20D",
            "2D",
            "100D",
            "100D2",
            "100D_200K",
            "100D_400K",
            "100D_800K",
            "100D_1000K",
        ]

        skip_seq = input("Do you want to skip the test with sequential code? (y/n): ")
        skip_cuda = input("Do you want to skip the test with CUDA code? (y/n): ")
        skip_omp_mpi = input("Do you want to skip the test with OMP_MPI code? (y/n): ")

        if skip_seq == "n":
            print("Running sequential test")
            print("-----------------------------------------")
            subprocess.run(["make", "KMEANS_seq"])
            self.main_test(dimensions, "seq")

        if skip_cuda == "n":
            print("Running CUDA test")
            print("-----------------------------------------")
            subprocess.run(["make", "KMEANS_cuda"])
            self.main_test(dimensions, "cuda")

        if skip_omp_mpi == "n":
            print("Running OMP test")
            print("-----------------------------------------")
            subprocess.run(["make", "KMEANS_omp_mpi"])
            self.main_test(dimensions, "omp_mpi")

        subprocess.run(["make", "clean"])


if __name__ == "__main__":
    unittest.main()
