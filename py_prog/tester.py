import unittest
import os
import subprocess

from run import main


# Function used to add AvgTime to csv file
def addAvgTime(test_type, avgTimes, pcs, thread):
    # Check if the path not exist
    if not os.path.exists(f"./test_csv/slurm/{test_type}_slurm.csv"):
        os.makedirs("./test_csv/slurm", exist_ok=True)
        # Create the file and write the header
        open(f"./test_csv/slurm/{test_type}_slurm.csv", "w").close()
        if test_type != "omp_mpi":
            subprocess.run(
                [
                    f"echo AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2 >> ./test_csv/slurm/{test_type}_slurm.csv"
                ],
                shell=True,
            )
        else:
            subprocess.run(
                [
                    f"echo Number of Process, Number of Thread, AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2 >> ./test_csv/slurm/{test_type}_slurm.csv"
                ],
                shell=True,
            )

    if test_type != "omp_mpi":
        subprocess.run(
            [
                f"echo {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]} >> ./test_csv/slurm/{test_type}_slurm.csv"
            ],
            shell=True,
        )
    else:
        subprocess.run(
            [
                f"echo {pcs} {thread} {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]} >> ./test_csv/slurm/{test_type}_slurm.csv"
            ],
            shell=True,
        )


class MyTest(unittest.TestCase):
    def doTest(self, vers: str, test: str, pcs: int, thread: int):
        self.assertEqual(main(vers, test, pcs, thread), True)

    def main_test(self, dimensions: list[str], vers: str):
        # Check the version of the program to run
        if vers == "seq":
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

                times = []

                # Open comp_time file and read all lines
                with open(f"./comp_time/{vers}/comp_time{dim}.csv", "r") as f:
                    times = f.readlines()

                # Convert all element in the array to float
                times = [float(time) for time in times]

                # AvgTime
                avgTime = sum(times) / len(times)
                avgTimes.append(avgTime)

            addAvgTime(vers, avgTimes, 0, 0)

    def test(self):
        dimensions = ["2D2", "10D", "20D", "2D", "100D", "100D2"]

        print("Running sequential test")
        print("-----------------------------------------")
        subprocess.run(["make", "KMEANS_seq"])
        self.main_test(dimensions, "seq")


if __name__ == "__main__":
    unittest.main()
