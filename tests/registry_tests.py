from mathblocks.blocks.grid import Grid
import mathblocks.blocks.registry as mr
import mathblocks.blocks.gameobjects as mo
import matplotlib.pyplot as plt
from mathblocks.blocks.constants import *
import numpy as np
import unittest

class RegisterTests(unittest.TestCase):
    def test_init(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        self.assertEqual(og_len, 3+len(reg.piles))
        self.assertTrue(reg.player in reg)
        self.assertTrue(reg.player in reg.coord_register)
        self.assertTrue(reg.button in reg)
        self.assertTrue(reg.button in reg.coord_register)
        self.assertTrue(reg.operator in reg)
        self.assertTrue(reg.operator in reg.coord_register)
        for pile in reg.piles.values():
            self.assertTrue(pile in reg)
            self.assertTrue(pile in reg.coord_register)

    def test_add_obj(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,3)
        not_coord = (0,0)
        new_obj = mo.GameObject(
            coord=coord,
            size=(1,1),
            color=1,
            obj_type="obj"
        )
        reg.add_obj(new_obj)
        self.assertTrue(new_obj in reg)
        self.assertTrue(new_obj in reg.coord_register)
        self.assertTrue(new_obj in reg.coord_register[coord])
        self.assertFalse(new_obj in reg.coord_register[not_coord])

    def test_add_obj_newcoord(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,3)
        not_coord = (0,0)
        new_obj = mo.GameObject(
            coord=not_coord,
            size=(1,1),
            color=1,
            obj_type="obj"
        )
        reg.add_obj(new_obj, coord)
        self.assertEqual(new_obj.coord, coord)
        self.assertTrue(new_obj in reg)
        self.assertTrue(new_obj in reg.coord_register)
        self.assertTrue(new_obj in reg.coord_register[coord])
        self.assertFalse(new_obj in reg.coord_register[not_coord])

    def test_add_block(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,3)
        not_coord = (0,0)
        new_obj = mo.Block(
            coord=coord,
            size=(1,1),
            color=1,
            val=1
        )
        reg.add_block(new_obj)
        self.assertTrue(new_obj in reg)
        self.assertTrue(new_obj in reg.coord_register)
        self.assertTrue(new_obj in reg.coord_register[coord])
        self.assertFalse(new_obj in reg.coord_register[not_coord])
        self.assertTrue(new_obj in reg.blocks)

    def test_add_block_newcoord(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,3)
        not_coord = (0,0)
        new_obj = mo.Block(
            coord=not_coord,
            size=(1,1),
            color=1,
            val=1
        )
        reg.add_obj(new_obj, coord)
        self.assertEqual(new_obj.coord, coord)
        self.assertTrue(new_obj in reg)
        self.assertTrue(new_obj in reg.coord_register)
        self.assertTrue(new_obj in reg.coord_register[coord])
        self.assertFalse(new_obj in reg.coord_register[not_coord])

    def test_make_eqn_1plus0(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        og_objs.remove(reg.operator)
        og_len = len(reg)
        left_val = 1
        right_val = 0
        operator = ADD
        reg.make_eqn(left_val, operator, right_val)
        new_objs = {*reg.left_eqn, *reg.right_eqn, reg.operator}
        self.assertEqual(len(reg), og_len + 1)
        self.assertEqual(reg.all_objs-og_objs, new_objs)

    def test_make_eqn_0plus1(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        og_objs.remove(reg.operator)
        og_len = len(reg)
        left_val = 0
        right_val = 1
        operator = ADD
        reg.make_eqn(left_val, operator, right_val)
        new_objs = {*reg.left_eqn, *reg.right_eqn, reg.operator}
        self.assertEqual(len(reg), og_len + 1)
        self.assertEqual(reg.all_objs-og_objs, new_objs)

    def test_make_eqn_1plus5(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        og_objs.remove(reg.operator)
        og_len = len(reg)
        left_val = 1
        right_val = 5
        operator = ADD
        reg.make_eqn(left_val, operator, right_val)
        new_objs = {*reg.left_eqn, *reg.right_eqn, reg.operator}
        self.assertEqual(len(reg), og_len + 2)
        self.assertEqual(reg.all_objs-og_objs, new_objs)

    def test_move_obj(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,3)
        new_coord = (0,0)
        new_obj = mo.GameObject(
            coord=coord,
            size=(1,1),
            color=1,
            obj_type="block1"
        )
        reg.add_obj(new_obj)
        reg.move_obj(new_obj, new_coord)
        self.assertEqual(new_obj.coord, new_coord)
        self.assertTrue(new_obj in reg[new_coord])

    def test_move_player(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,3)
        old_coord = (0,0)
        reg.move_obj(reg.player, coord)

        reg.move_player(STAY)
        self.assertEqual(reg.player.coord, coord)
        self.assertTrue(reg.player in reg[coord])
        self.assertFalse(reg.player in reg[old_coord])
        old_coord = reg.player.coord

        reg.move_player(UP)
        coord = (coord[0]-1, coord[1])
        self.assertEqual(reg.player.coord, coord)
        self.assertTrue(reg.player in reg[coord])
        self.assertFalse(reg.player in reg[old_coord])
        old_coord = reg.player.coord

        reg.move_player(RIGHT)
        coord = (coord[0], coord[1]+1)
        self.assertEqual(reg.player.coord, coord)
        self.assertTrue(reg.player in reg[coord])
        self.assertFalse(reg.player in reg[old_coord])
        old_coord = reg.player.coord

        reg.move_player(DOWN)
        coord = (coord[0]+1, coord[1])
        self.assertEqual(reg.player.coord, coord)
        self.assertTrue(reg.player in reg[coord])
        self.assertFalse(reg.player in reg[old_coord])
        old_coord = reg.player.coord

        reg.move_player(LEFT)
        coord = (coord[0], coord[1]-1)
        self.assertEqual(reg.player.coord, coord)
        self.assertTrue(reg.player in reg[coord])
        self.assertFalse(reg.player in reg[old_coord])

    def test_make_block(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,4)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=1
        )
        self.assertEqual(new_block.coord, coord)
        self.assertTrue(new_block in reg[coord])

    def test_handle_grab(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (3,4)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=1
        )
        reg.move_obj(reg.player, coord)
        reg.handle_grab()
        self.assertEqual(new_block.coord, reg.player.coord)
        self.assertTrue(reg.player.is_holding)
        self.assertEqual(reg.player.held_obj, new_block)

    def test_handle_grab_pile1(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertTrue(len(reg.blocks) == 1)
        self.assertTrue(new_block in reg.blocks)
        self.assertEqual(new_block.val, pilenum)

    def test_handle_grab_pile5(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        pilenum = 5
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertTrue(len(reg.blocks) == 1)
        self.assertTrue(new_block in reg.blocks)
        self.assertEqual(new_block.val, pilenum)

    def test_handle_grab_pile10(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        pilenum = 10
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertTrue(len(reg.blocks) == 1)
        self.assertTrue(new_block in reg.blocks)
        self.assertEqual(new_block.val, pilenum)

    def test_handle_grab_pile50(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        pilenum = 10
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertTrue(len(reg.blocks) == 1)
        self.assertTrue(new_block in reg.blocks)
        self.assertEqual(new_block.val, pilenum)

    def test_handle_grab_pile100(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_objs = {*reg.all_objs}
        pilenum = 100
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertTrue(len(reg.blocks) == 1)
        self.assertTrue(new_block in reg.blocks)
        self.assertEqual(new_block.val, pilenum)

    def test_handle_move_up(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(UP)
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertEqual(new_block.coord, reg.player.coord)
        self.assertTrue(new_block in reg[reg.player.coord])
        self.assertFalse(new_block in reg[coord])

    def test_handle_move_right(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertEqual(new_block.coord, reg.player.coord)
        self.assertTrue(new_block in reg[reg.player.coord])
        self.assertFalse(new_block in reg[coord])

    def test_handle_move_left(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(LEFT)
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertEqual(new_block.coord, reg.player.coord)
        self.assertTrue(new_block in reg[reg.player.coord])
        self.assertFalse(new_block in reg[coord])

    def test_handle_move_down(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(DOWN)
        self.assertEqual(new_block, reg.player.held_obj)
        self.assertEqual(new_block.coord, reg.player.coord)
        self.assertTrue(new_block in reg[reg.player.coord])
        self.assertFalse(new_block in reg[coord])

    def test_handle_drop(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (3,4)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.handle_drop()
        self.assertNotEqual(new_block, reg.player.held_obj)
        self.assertEqual(new_block.coord, reg.player.coord)
        self.assertTrue(new_block in reg[reg.player.coord])
        self.assertFalse(new_block in reg[coord])
        self.assertTrue(reg.player in reg[reg.player.coord])
        self.assertFalse(reg.player in reg[coord])
        coord = reg.player.coord
        reg.move_player(RIGHT)
        self.assertNotEqual(new_block, reg.player.held_obj)
        self.assertNotEqual(new_block.coord, reg.player.coord)
        self.assertFalse(new_block in reg[reg.player.coord])
        self.assertTrue(new_block in reg[coord])
        self.assertFalse(reg.player in reg[coord])

    def test_handle_drop100(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 100
        pile = reg.piles[PILE+str(pilenum)]
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.handle_drop()
        self.assertNotEqual(new_block, reg.player.held_obj)
        self.assertEqual(new_block.coord, reg.player.coord)
        self.assertTrue(new_block in reg[reg.player.coord])
        self.assertFalse(new_block in reg[coord])
        self.assertTrue(reg.player in reg[reg.player.coord])
        self.assertFalse(reg.player in reg[coord])
        coord = reg.player.coord
        reg.move_player(RIGHT)
        self.assertNotEqual(new_block, reg.player.held_obj)
        self.assertNotEqual(new_block.coord, reg.player.coord)
        self.assertTrue(new_block in reg[reg.player.coord])
        self.assertTrue(new_block in reg[coord])
        self.assertFalse(reg.player in reg[coord])
        reg.move_player(UP)
        self.assertNotEqual(new_block.coord, reg.player.coord)
        self.assertFalse(new_block in reg[reg.player.coord])
        self.assertTrue(new_block in reg[coord])
        self.assertFalse(reg.player in reg[coord])

    def test_handle_drop_pile1(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.move_obj(pile, reg.player.coord)
        reg.handle_drop()
        self.assertFalse(new_block in reg)
        self.assertTrue(reg.player in reg)
        self.assertEqual(pile.coord, reg.player.coord)

    def test_handle_drop_pile5(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 5
        pile = reg.piles[PILE+str(pilenum)]
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.move_obj(pile, reg.player.coord)
        reg.handle_drop()
        self.assertFalse(new_block in reg)
        self.assertTrue(reg.player in reg)
        self.assertEqual(pile.coord, reg.player.coord)

    def test_handle_drop_pile10(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 10
        pile = reg.piles[PILE+str(pilenum)]
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.move_obj(pile, reg.player.coord)
        reg.handle_drop()
        self.assertFalse(new_block in reg)
        self.assertTrue(reg.player in reg)
        self.assertEqual(pile.coord, reg.player.coord)

    def test_handle_drop_pile50(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 50
        pile = reg.piles[PILE+str(pilenum)]
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.move_obj(pile, reg.player.coord)
        reg.handle_drop()
        self.assertFalse(new_block in reg)
        self.assertTrue(reg.player in reg)
        self.assertEqual(pile.coord, reg.player.coord)

    def test_handle_drop_pile100(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 100
        pile = reg.piles[PILE+str(pilenum)]
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.move_obj(pile, reg.player.coord)
        reg.handle_drop()
        self.assertFalse(new_block in reg)
        self.assertTrue(reg.player in reg)
        self.assertEqual(pile.coord, reg.player.coord)

    def test_handle_drop_button(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        pilenum = 1
        pile = reg.piles[PILE+str(pilenum)]
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        reg.move_obj(pile, coord)
        reg.handle_grab()
        new_block = next(iter(reg.blocks))
        reg.move_player(RIGHT)
        reg.move_obj(reg.button, reg.player.coord)
        reg.handle_drop()
        self.assertFalse(new_block in reg[reg.player.coord])
        self.assertFalse(reg.button.coord == new_block.coord)
        self.assertEqual(reg.button.coord, reg.player.coord)
        new_coord = (reg.player.coord[0]+reg.button.size[0], reg.button.coord[1])
        self.assertEqual(new_block.coord, new_coord)
        self.assertTrue(new_block in reg[new_coord])

    def test_decompose_obj1(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (1,1)
        og_len = len(reg)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=1
        )
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        reg.decompose_obj(new_block)
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)

    def test_decompose_obj1(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        coord = (1,1)
        og_len = len(reg)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=1
        )
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        reg.decompose_obj(new_block)
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)

    def test_decompose_obj5(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        block_val = 5
        new_val = 1
        new_len = 5
        coord = (1,1)
        og_len = len(reg)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=block_val
        )
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        reg.decompose_obj(new_block)
        self.assertEqual(len(reg), og_len + new_len)
        self.assertFalse(new_block in reg)
        for block in reg.blocks:
            self.assertEqual(block.val, new_val)
        self.assertEqual(len(reg.blocks), new_len)

    def test_decompose_obj10(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        block_val = 10
        new_val = 5
        new_len = 2
        coord = (1,1)
        og_len = len(reg)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=block_val
        )
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        reg.decompose_obj(new_block)
        self.assertEqual(len(reg), og_len + new_len)
        self.assertFalse(new_block in reg)
        for block in reg.blocks:
            self.assertEqual(block.val, new_val)
        self.assertEqual(len(reg.blocks), new_len)

    def test_decompose_obj50(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        block_val = 50
        new_val = 10
        new_len = 5
        coord = (1,1)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=block_val
        )
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        reg.decompose_obj(new_block)
        #self.assertEqual(len(reg), og_len + new_len)
        self.assertFalse(new_block in reg)
        for block in reg.blocks:
            self.assertEqual(block.val, new_val)
        self.assertEqual(len(reg.blocks), new_len)

    def test_decompose_obj100(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        block_val = 100
        new_val = 50
        new_len = 2
        coord = (1,1)
        og_len = len(reg)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=block_val
        )
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        reg.decompose_obj(new_block)
        self.assertEqual(len(reg), og_len + new_len)
        self.assertFalse(new_block in reg)
        for block in reg.blocks:
            self.assertEqual(block.val, new_val)
        self.assertEqual(len(reg.blocks), new_len)

    def test_handle_decomp(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        coord = (1,1)
        reg.move_obj(reg.player, coord)
        new_block = reg.make_block(
            coord=coord,
            size=(1,1),
            color=1,
            val=1
        )
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        reg.handle_grab()
        reg.handle_decomp()
        self.assertEqual(len(reg), og_len + 1)
        self.assertTrue(new_block in reg)
        self.assertTrue(reg.player.held_obj is None)

    def test_merge1(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        coord = (1,1)
        bv = 1
        mv = 5
        new_blocks = set()
        for i in range(mv//bv):
            new_block = reg.make_block(
                coord=coord,
                size=(1,1),
                color=1,
                val=bv
            )
            new_blocks.add(new_block)
        self.assertEqual(len(reg), og_len + mv//bv)
        reg.merge(reg.blocks, mv)
        self.assertTrue(new_block not in reg)
        self.assertEqual(len(reg), og_len + 1)
        for block in new_blocks:
            self.assertTrue(block not in reg)
        self.assertEqual(next(iter(reg.blocks)).val, mv)

    def test_merge5(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        coord = (1,1)
        bv = 5
        mv = 10
        change_len = mv//bv-1
        new_blocks = set()
        for i in range(mv//bv):
            new_block = reg.make_block(
                coord=coord,
                size=(1,1),
                color=1,
                val=bv
            )
            new_blocks.add(new_block)
        self.assertEqual(len(reg), og_len + mv//bv)
        reg.merge(reg.blocks, mv)
        self.assertTrue(new_block not in reg)
        self.assertEqual(len(reg), og_len + 1)
        for block in new_blocks:
            self.assertTrue(block not in reg)
        self.assertEqual(next(iter(reg.blocks)).val, mv)

    def test_merge10(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        coord = (1,1)
        bv = 10
        mv = 50
        change_len = mv//bv-1
        new_blocks = set()
        for i in range(mv//bv):
            new_block = reg.make_block(
                coord=coord,
                size=(1,1),
                color=1,
                val=bv
            )
            new_blocks.add(new_block)
        self.assertEqual(len(reg), og_len + mv//bv)
        reg.merge(reg.blocks, mv)
        self.assertTrue(new_block not in reg)
        self.assertEqual(len(reg), og_len + 1)
        for block in new_blocks:
            self.assertTrue(block not in reg)
        self.assertEqual(next(iter(reg.blocks)).val, mv)

    def test_merge50(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        coord = (1,1)
        bv = 50
        mv = 100
        change_len = mv//bv-1
        new_blocks = set()
        for i in range(mv//bv):
            new_block = reg.make_block(
                coord=coord,
                size=(1,1),
                color=1,
                val=bv
            )
            new_blocks.add(new_block)
        self.assertEqual(len(reg), og_len + mv//bv)
        reg.merge(reg.blocks, mv)
        self.assertTrue(new_block not in reg)
        self.assertEqual(len(reg), og_len + 1)
        for block in new_blocks:
            self.assertTrue(block not in reg)
        self.assertEqual(next(iter(reg.blocks)).val, mv)

    def test_merge100(self):
        grid = Grid((50,50), 1, divide=True)
        reg = mr.Register(grid)
        og_len = len(reg)
        coord = (1,1)
        bv = 100
        mv = 500
        new_blocks = set()
        for i in range(mv//bv):
            new_block = reg.make_block(
                coord=coord,
                size=(1,1),
                color=1,
                val=bv
            )
            new_blocks.add(new_block)
        reg.merge(reg.blocks, mv)
        self.assertEqual(len(reg), og_len + len(new_blocks))
        for block in new_blocks:
            self.assertTrue(block in reg)
            self.assertTrue(block.val == bv)

if __name__ == "__main__":
    unittest.main()
    ### Test placing objects ontop of eachother no button
    ##grid = Grid((50,50), 1, divide=True)
    ##register = mr.Register(grid)
    ##coord = (5,5)
    ##for val in BLOCK_VALS[:-1]:
    ##    register.clear_blocks()
    ##    for i in range(4):
    ##        btype = BLOCK+str(val)
    ##        block = mr.Block(
    ##            color=COLORS[btype],
    ##            coord=coord,
    ##            size=BLOCK_SIZES[val],
    ##            val=val
    ##        )
    ##        register.add_obj(block, coord)
    ##    register.draw_register()
    ##    plt.imshow(register.grid.grid)
    ##    plt.show()
    ##    block = mr.Block(
    ##        color=COLORS[btype],
    ##        coord=coord,
    ##        size=BLOCK_SIZES[val],
    ##        val=val
    ##    )
    ##    register.add_obj(block)
    ##    register.attempt_merge(block.coord)
    ##    register.draw_register()
    ##    plt.imshow(register.grid.grid)
    ##    plt.show()


    ###for i,j in zip(range(1,106,5), range(105, 1, -2)):
    ###    register.set_nonblocks()
    ###    register.make_eqn(i, ADD, j)
    ###    register.draw_register()
    ###    assert register.eqn_solution == i+j
    ###    plt.imshow(register.grid.grid)
    ###    plt.show()

    ###for i,j in zip(range(1,51,5), range(50, 1, -2)):
    ###    register.set_nonblocks()
    ###    register.make_eqn(i, SUBTRACT, j)
    ###    register.draw_register()
    ###    assert register.eqn_solution == i-j
    ###    plt.imshow(register.grid.grid)
    ###    plt.show()

    ###for i,j in zip(range(1,51,5), range(50, 1, -2)):
    ###    register.set_nonblocks()
    ###    register.make_eqn(i, MULTIPLY, j)
    ###    register.draw_register()
    ###    assert register.eqn_solution == i*j
    ###    plt.imshow(register.grid.grid)
    ###    plt.show()

