import unittest
import os
import subprocess

from run import run_test


# Function used to add AvgTime to csv file
def addAvgTime(test_type, dimension, avgTime):
    # Check if the path not exist
    if os.path.exists(f"./{test_type}.csv") == False:
        open(f"./{test_type}.csv", "w").close()
        subprocess.run(
            [f"echo Test dimension, AvgTime >> ./{test_type}.csv"], shell=True
        )

    subprocess.run([f"echo {dimension}, {avgTime} >> ./{test_type}.csv"], shell=True)


class MyTest(unittest.TestCase):
    def doTest(self, test_type, dimension):
        self.assertEqual(run_test(test_type, dimension), True)

    def test(self):
        test_type = input("Enter test type: ")
        dimensions = ["2D2", "10D", "20D", "2D", "100D", "100D2"]

        for dimension in dimensions:
            # Remove comp_time files if exist
            if os.path.exists(f"comp_time/{test_type}/comp_time{dimension}.csv"):
                os.remove(f"comp_time/{test_type}/comp_time{dimension}.csv")

            # Create comp_time files
            open(f"comp_time/{test_type}/comp_time{dimension}.csv", "w").close()

            for _ in range(50):
                self.doTest(test_type, dimension)

            times = []

            # Open comp_time file and read all lines
            with open(f"comp_time/{test_type}/comp_time{dimension}.csv", "r") as f:
                times = f.readlines()

            # Convert all element in the array to float
            times = [float(time) for time in times]

            # AvgTime
            avgTime = sum(times) / len(times)
            addAvgTime(test_type, dimension, avgTime)


if __name__ == "__main__":
    unittest.main()
