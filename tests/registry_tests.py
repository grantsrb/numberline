from numberline.grid import Grid
from numberline.registry import Register
from numberline.constants import *
import numpy as np
import matplotlib.pyplot as plt
import unittest

class RegisterTests(unittest.TestCase):
    def test_init(self):
        grid = Grid(1)
        reg = Register(grid)

    def test_get_markers(self):
        grid = Grid(1)
        reg = Register(grid)
        cols, colors = reg.get_markers()
        goal_cols = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100}
        for col,color in zip(cols, colors):
            self.assertTrue(col in goal_cols)
            if col == 100:
                self.assertEqual(color, 2*COLORS[MARKER])
            else:
                self.assertEqual(color, COLORS[MARKER])

    def test_translate_neg1(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)
        g = grid.grid

        reg.translate(-1)
        reg.draw_register()
        g2 = grid.grid
        self.assertTrue(np.array_equal(
            g[:, :-5*density],
            g2[:, density:-4*density]
        ))

    def test_translate_pos1(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)
        g = grid.grid

        reg.translate(1)
        reg.draw_register()
        g2 = grid.grid
        self.assertTrue(np.array_equal(
            g2[:, :-5*density],
            g[:, density:-4*density]
        ))

    def test_translate_neg7(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)
        g = grid.grid

        reg.translate(-7)
        reg.draw_register()
        g2 = grid.grid
        self.assertTrue(np.array_equal(
            g[:, :-11*density],
            g2[:, 7*density:-4*density]
        ))

    def test_translate_pos7(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)
        g = grid.grid

        reg.translate(7)
        reg.draw_register()
        g2 = grid.grid
        self.assertTrue(np.array_equal(
            g2[:, :-11*density],
            g[:, 7*density:-4*density]
        ))

    def test_translate_neg7_pos10(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)
        g = grid.grid

        reg.translate(-7)
        reg.draw_register()
        reg.translate(10)
        reg.draw_register()
        g2 = grid.grid
        self.assertTrue(np.array_equal(
            g[:, 3*density:-4*density],
            g2[:, :-7*density]
        ))

    def test_zoom_in(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)

        reg.zoom_in()
        reg.translate(25)
        reg.draw_register()
        self.assertEqual(reg.trans, 525)
        g = grid.grid
        self.assertTrue(len(g[g==COLORS[ZERO]]) == 0)
        self.assertEqual(len(g[g==2*COLORS[MARKER]]), (density-1)**2)

    def test_zoom_out(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)

        reg.zoom_out()
        reg.translate(-5)
        reg.draw_register()
        self.assertEqual(reg.trans, 0)
        g = grid.grid
        self.assertEqual(grid[grid.middle], COLORS[ZERO])
        self.assertEqual(grid[grid.zoom_idx], 1/10)

    def test_fill_positive(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)

        fill = 9
        reg.add_fill(fill)
        reg.draw_register()
        g = grid.grid[0,:(fill+1)*density]
        self.assertEqual(len(g[g==COLORS[FILL]]), fill*(density-1))
        self.assertEqual(len(g[g==COLORS[ZERO]]), (density-1))
        self.assertEqual(len(g[g==COLORS[DEFAULT]]), fill+1)

        plus = 10
        reg.add_fill(plus)
        total = plus + fill
        reg.draw_register()
        g = grid.grid[0,:(total+1)*density]
        self.assertEqual(len(g[g==COLORS[FILL]]), (total-1)*(density-1))
        self.assertEqual(len(g[g==(COLORS[FILL]+COLORS[MARKER])]), (density-1))
        self.assertEqual(len(g[g==COLORS[ZERO]]), (density-1))
        self.assertEqual(len(g[g==COLORS[DEFAULT]]), total+1)

    def test_fill_negative(self):
        density = 10
        grid = Grid(density)
        reg = Register(grid)

        fill = -9
        reg.add_fill(fill)
        before = grid.grid
        reg.draw_register()
        self.assertTrue(np.array_equal(before, grid.grid))

        reg.translate(-10)
        reg.draw_register()
        g = grid.grid[0, :20*density]
        self.assertEqual(g[0], COLORS[MARKER])
        self.assertEqual(len(g[g==COLORS[FILL]]), (-fill)*(density-1))
        self.assertEqual(len(g[g==COLORS[ZERO]]), (density-1))
        self.assertEqual(g[11*density:].sum(), 0)



if __name__ == "__main__":
    unittest.main()
