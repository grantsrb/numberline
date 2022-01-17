from mathblocks.blocks.grid import Grid
import mathblocks.blocks.registry as mr
import mathblocks.blocks.gameobjects as mo
from mathblocks.blocks.constants import *
import mathblocks.blocks.ai as ma
import matplotlib.pyplot as plt
import numpy as np
import unittest

class RegisterTests(unittest.TestCase):
    def test_get_removal_block(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        reg._targ_val = 2
        reg.move_obj(reg.player, (2,2))
        b1 = reg.make_block(
            coord=(2,10),
            size=(1,1),
            color=1,
            val=1
        )
        b2 = reg.make_block(
            coord=(10,2),
            size=(1,1),
            color=1,
            val=1
        )
        b3 = reg.make_block(
            coord=(2,3),
            size=(1,1),
            color=1,
            val=1
        )
        self.assertEqual(b3, ma.get_removal_block(reg))

    def test_get_removal_block_sameloc(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        reg._targ_val = 2
        reg.move_obj(reg.player, (2,2))
        b1 = reg.make_block(
            coord=(2,10),
            size=(1,1),
            color=1,
            val=1
        )
        b2 = reg.make_block(
            coord=(2, 10),
            size=(1,1),
            color=1,
            val=1
        )
        b3 = reg.make_block(
            coord=(2,10),
            size=(1,1),
            color=1,
            val=1
        )
        objs = {b1,b2,b3}
        self.assertTrue(ma.get_removal_block(reg) in objs)

    def test_get_removal_block_large(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        reg._targ_val = 11
        reg.move_obj(reg.player, (2,2))
        b1 = reg.make_block(
            coord=(2,10),
            size=(1,1),
            color=1,
            val=50
        )
        b2 = reg.make_block(
            coord=(2, 10),
            size=(1,1),
            color=1,
            val=1
        )
        b3 = reg.make_block(
            coord=(2,10),
            size=(1,1),
            color=1,
            val=1
        )
        self.assertEqual(ma.get_removal_block(reg), b1)

if __name__=="__main__":
    unittest.main()
