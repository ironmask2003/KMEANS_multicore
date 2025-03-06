import unittest

from run import run_test

ciao = []


class MyTest(unittest.TestCase):
    def test_mpi100D(self):
        self.assertEqual(run_test("mpi", "100D", ciao), True)


if __name__ == "__main__":
    unittest.main()
