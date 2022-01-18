import numberline.utils as utils
import unittest

class UtilsTests(unittest.TestCase):
    def test_get_magnitude_counts(self):
        vals = [1, -1, 2, 123, 123.45, 0.1708, -69.001]
        solns = [
            {0: 1},
            {0: 1},
            {0: 2},
            {2: 1, 1: 2, 0: 3},
            {2: 1, 1: 2, 0: 3, -1: 4, -2: 5},
            {-1: 1, -2: 7, -4: 8},
            {1: 6, 0: 9, -3: 1},
        ]
        for val,soln in zip(vals, solns):
            counts = utils.get_magnitude_counts(val)
            for k in soln.keys():
                self.assertEqual(soln[k], counts[k])
            for k in counts.keys():
                self.assertEqual(soln[k], counts[k])


if __name__=="__main__":
    unittest.main()
