from numberline.grid import Grid
import matplotlib.pyplot as plt
from numberline.constants import *
import numpy as np
import unittest

class TestGrid(unittest.TestCase):
    def test_init(self):
        grid = Grid(unit_density=1)
        self.assertEqual(grid.shape, (1,101))
        self.assertEqual(grid.pixel_shape, (1,101))
        self.assertEqual(grid.raw_shape, (1, 105))

    def test_middle(self):
        grid = Grid(unit_density=10)
        self.assertEqual(grid.middle, 50)
        self.assertEqual(grid.middle_row, 0)

    def test_getitem(self):
        grid = Grid(unit_density=10)
        self.assertEqual(grid[(0,0)], 0)
        self.assertEqual(grid[0,0], 0)
        self.assertEqual(grid[0], 0)
        self.assertEqual(grid[(0,10)], 0)
        self.assertEqual(grid[0,10], 0)
        self.assertEqual(grid[10], 0)

        grid._grid[:,:] = 10
        self.assertEqual(grid[(0,10)], 10)
        self.assertEqual(grid[0,10], 10)
        self.assertEqual(grid[10], 10)

    def test_units2pixels(self):
        density = 1
        grid = Grid(unit_density=density)
        coords = [(1,1), (0,9), (7,0), (100,100)]
        solns = [*coords]
        for coord,soln in zip(coords,solns):
            pred = grid.units2pixels(coord)
            self.assertEqual(pred, soln)

        density = 7
        grid = Grid(unit_density=density)
        coords = [(1,1), (0,9), (7,0), (100,100)]
        solns = [(7,7), (0, 63), (49, 0), (700,700)]
        for coord,soln in zip(coords,solns):
            pred = grid.units2pixels(coord)
            self.assertEqual(pred, soln)

    def test_pixels2units(self):
        density = 1
        grid = Grid(unit_density=density)
        coords = [(1,1), (0,9), (7,0), (100,100)]
        solns = [*coords]
        for coord,soln in zip(coords,solns):
            pred = grid.pixels2units(coord)
            self.assertEqual(pred, soln)

        density = 7
        grid = Grid(unit_density=density)
        coords = [(11,9), (0, 63), (53, 5), (704,700)]
        solns = [(1,1), (0,9), (7,0), (100,100)]
        for coord,soln in zip(coords,solns):
            pred = grid.pixels2units(coord)
            self.assertEqual(pred, soln)

    def test_draw(self):
        grid = Grid(unit_density=10)
        self.assertEqual(grid[(0,0)], 0)
        self.assertEqual(grid[(0,1)], 0)
        self.assertEqual(grid._grid[0,9], 0)
        self.assertEqual(grid._grid[9,9], 0)
        grid.draw((0,0), color=1)
        self.assertEqual(grid[(0,0)], 1)
        self.assertEqual(grid[(0,1)], 0)
        self.assertEqual(grid._grid[0,9], 0)
        self.assertEqual(grid._grid[9,9], 0)

    def test_setitem(self):
        grid = Grid(unit_density=10)
        self.assertEqual(grid[(0,0)], 0)
        self.assertEqual(grid[(0,1)], 0)
        self.assertEqual(grid._grid[0,9], 0)
        self.assertEqual(grid._grid[9,9], 0)
        grid[0,0] = 1
        self.assertEqual(grid[(0,0)], 1)
        self.assertEqual(grid[(0,1)], 0)
        self.assertEqual(grid._grid[0,9], 0)
        self.assertEqual(grid._grid[9,9], 0)
        grid[0] = 2
        self.assertEqual(grid[(0,0)], 2)
        self.assertEqual(grid[(0,1)], 0)
        self.assertEqual(grid._grid[0,9], 0)
        self.assertEqual(grid._grid[9,9], 0)

    def test_slice_draw(self):
        grid = Grid(unit_density=10)
        grid.slice_draw((0,0), (1,1), color=1)
        self.assertEqual(grid[(0,0)], 1)
        self.assertEqual(grid[(0,1)], 0)
        self.assertEqual(grid._grid[0,9], 0)
        self.assertEqual(grid._grid[9,9], 0)

        grid = Grid(unit_density=10)
        grid.slice_draw((0,0), (1,10), color=1)
        for i in range(10):
            self.assertEqual(grid[0,i], 1)
            self.assertEqual(grid._grid[0,10*i+9], 0)

        self.assertEqual(grid._grid[9,0], 0)
        self.assertEqual(grid[0,10], 0)


if __name__=="__main__":
    unittest.main()
