import mathblocks.blocks.utils as utils
import unittest

class UtilsTests(unittest.TestCase):
    def test_decompose(self):
        atoms = [1,3,7,15]
        vals = [0, 1, 2, 3, 13, 17, 69]
        solns = [
            {1:0, 3: 0, 7: 0, 15: 0},
            {1:1, 3: 0, 7: 0, 15: 0},
            {1:2, 3: 0, 7: 0, 15: 0},
            {1:0, 3: 1, 7: 0, 15: 0},
            {1:0, 3: 2, 7: 1, 15: 0},
            {1:2, 3: 0, 7: 0, 15: 1},
            {1:2, 3: 0, 7: 1, 15: 4},
        ]
        for val,soln in zip(vals, solns):
            counts = utils.decompose(val, atoms)
            for k in soln.keys():
                self.assertEqual(soln[k], counts[k])


if __name__=="__main__":
    unittest.main()
