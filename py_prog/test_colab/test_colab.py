import unittest
import os
import subprocess

from run_colab import main


# Function used to add AvgTime to csv file
def addAvgTime(test_type, avgTimes):
    # Check if the path not exist
    if not os.path.exists(f"./{test_type}.csv"):
        # Create the file and write the header
        open(f"./{test_type}.csv", "w").close()
        subprocess.run(
            [
                f"echo AvgTime2D2, AvgTime10D, AvgTime20D, AvgTime2D, AvgTime100D, AvgTime100D2 >> ./{test_type}.csv"
            ],
            shell=True,
        )

    subprocess.run(
        [
            f"echo {avgTimes[0]}, {avgTimes[1]}, {avgTimes[2]}, {avgTimes[3]}, {avgTimes[4]}, {avgTimes[5]} >> ./{test_type}.csv"
        ],
        shell=True,
    )


class ColabTest(unittest.TestCase):
    def doTest(self, vers, test):
        main(vers, test)

    def test(self):
        test_type = input("Enter test type: ")
        subprocess.run(["make", f"KMEANS_{test_type}"])
        dimensions = ["2D2", "10D", "20D", "2D", "100D", "100D2"]

        avgTimes = []

        for dim in dimensions:
            # Remove comp_time files if exist
            if os.path.exists(f"./comp_time/{test_type}/comp_time{dim}.csv"):
                os.remove(f"./comp_time/{test_type}/comp_time{dim}.csv")

            # Create comp_time files
            open(f"./comp_time/{test_type}/comp_time{dim}.csv", "w").close()
            for _ in range(25):
                self.doTest(test_type, dim)
            # Array to store all times
            times = []

            # Open comp_time file and read all lines
            with open(f"./comp_time/{test_type}/comp_time{dim}.csv", "r") as f:
                times = f.readlines()

            # Convert all element in the array to float
            times = [float(time) for time in times]

            # AvgTime
            avgTime = sum(times) / len(times)
            avgTimes.append(avgTime)

        addAvgTime(test_type, avgTimes)


if __name__ == "__main__":
    unittest.main()
