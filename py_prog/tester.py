import unittest
import os

from run import run_test


class MyTest(unittest.TestCase):
    def test(self):
        test_type = input("Enter test type: ")
        dimension = input("Enter dimension: ")

        # Remove comp_time files if exist
        if os.path.exists(f"comp_time/{test_type}/comp_time{dimension}.csv"):
            os.remove(f"comp_time/{test_type}/comp_time{dimension}.csv")

        # Create comp_time files
        open(f"comp_time/{test_type}/comp_time{dimension}.csv", "w").close()

        for _ in range(50):
            self.assertEqual(run_test(test_type, dimension, []), True)


if __name__ == "__main__":
    unittest.main()
