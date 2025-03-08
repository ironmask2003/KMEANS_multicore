import unittest
import os
import subprocess

from run import run_test


# Function used to add AvgTime to csv file
def addAvgTime(test_type, dimension, avgTime, num_process, num_thread):
    # Check if the path not exist
    if not os.path.exists(f"./{test_type}.csv"):
        # Create the file and write the header
        open(f"./{test_type}.csv", "w").close()
        subprocess.run(
            [
                f"echo Test dimension, Number of Process, Number of thread, AvgTime >> ./{test_type}.csv"
            ],
            shell=True,
        )

    # Write in the final csv file the AvgTime of the test
    subprocess.run(
        [
            f"echo {dimension}, {num_process}, {num_thread}, {avgTime} >> ./{test_type}.csv"
        ],
        shell=True,
    )


class MyTest(unittest.TestCase):
    # Function to run the test
    def doTest(self, test_type, dimension, num_process, num_thread):
        self.assertEqual(run_test(test_type, dimension, num_process, num_thread), True)

    # Function to test the CUDA version
    def test_cuda(self):
        test_type = "cuda"
        dimensions = ["2D2", "10D", "20D", "2D", "100D", "100D2"]

        for dimension in dimensions:
            # Remove comp_time files if exist
            if os.path.exists(f"comp_time/{test_type}/comp_time{dimension}.csv"):
                os.remove(f"comp_time/{test_type}/comp_time{dimension}.csv")

            # Create comp_time files
            open(f"comp_time/{test_type}/comp_time{dimension}.csv", "w").close()

            for _ in range(50):
                self.doTest(
                    test_type, dimension, 0, 0
                )  # Set num_process and num_thread to 0 fo test cuda

            # Array to store all times
            times = []

            # Open comp_time file and read all lines
            with open(f"comp_time/{test_type}/comp_time{dimension}.csv", "r") as f:
                times = f.readlines()

            # Convert all element in the array to float
            times = [float(time) for time in times]

            # AvgTime
            avgTime = sum(times) / len(times)
            addAvgTime(test_type, dimension, avgTime, 0, 0)

    # Main function to run the test
    def test(self):
        test_type = input("Enter test type: ")

        # Check if the test is with cuda
        if test_type == "cuda":
            return self.test_cuda()

        # Else test with OMP+MPI
        dimensions = ["2D2", "10D", "20D", "2D", "100D", "100D2"]
        num_process = [1, 2, 4, 8, 16, 32]
        num_threads = [1, 2, 4, 8, 16, 32]

        for proc, thread, dimension in [
            (p, t, d) for p in num_process for t in num_threads for d in dimensions
        ]:
            # Remove comp_time files if exist
            if os.path.exists(f"comp_time/{test_type}/comp_time{dimension}.csv"):
                os.remove(f"comp_time/{test_type}/comp_time{dimension}.csv")

            # Create comp_time files
            open(f"comp_time/{test_type}/comp_time{dimension}.csv", "w").close()

            for _ in range(50):
                self.doTest(test_type, dimension, proc, thread)

            # Array to store all times
            times = []

            # Open comp_time file and read all lines
            with open(f"comp_time/{test_type}/comp_time{dimension}.csv", "r") as f:
                times = f.readlines()

            # Convert all element in the array to float
            times = [float(time) for time in times]

            # AvgTime
            avgTime = sum(times) / len(times)
            addAvgTime(test_type, dimension, avgTime, proc, thread)


if __name__ == "__main__":
    unittest.main()
