import mathblocks.blocks.registry as reg
from mathblocks.blocks.utils import coord_diff, coord_add
import numpy as np
import unittest

class PlayerTests(unittest.TestCase):

    def test_coord_no_grab(self):
        icoord = (7,4)
        coords = [(0,0), (1,1), (10, 100)]
        for coord in coords:
            player = reg.PlayerObject(
                obj_type="player",
                color=1,
                coord=icoord,
                size=(1,1)
            )
            self.assertEqual(player.player_coord, icoord)
            self.assertEqual(player.coord, icoord)
            player.coord = coord
            self.assertEqual(player.player_coord, coord)
            self.assertEqual(player.coord, coord)

    def test_grab(self):
        coords = [(-1,0), (1,1), (10, 100)]
        icoords = [(-1,1), (5,2), (9, 69)]
        for coord,icoord in zip(coords, icoords):
            player = reg.PlayerObject(
                obj_type="player",
                color=1,
                coord=coord,
                size=(1,1)
            )
            item = reg.PlayerObject(
                obj_type="item",
                color=1,
                coord=icoord,
                size=(2,5)
            )
            player.grab(item)
            self.assertEqual(player.grabbed_obj, item)

    def test_is_grabbing(self):
        coords = [(-1,0), (1,1), (10, 100)]
        icoords = [(-1,1), (5,2), (9, 69)]
        for coord,icoord in zip(coords, icoords):
            player = reg.PlayerObject(
                obj_type="player",
                color=1,
                coord=coord,
                size=(1,1)
            )
            item = reg.PlayerObject(
                obj_type="item",
                color=1,
                coord=icoord,
                size=(2,5)
            )
            self.assertFalse(player.is_grabbing)
            player.grab(item)
            self.assertTrue(player.is_grabbing)
            player.grabbed_obj = None
            self.assertFalse(player.is_grabbing)

    def test_drop(self):
        coords = [(-1,0), (1,1), (10, 100)]
        icoords = [(-1,1), (5,2), (9, 69)]
        for coord,icoord in zip(coords, icoords):
            player = reg.PlayerObject(
                obj_type="player",
                color=1,
                coord=coord,
                size=(1,1)
            )
            item = reg.PlayerObject(
                obj_type="item",
                color=1,
                coord=icoord,
                size=(2,5)
            )
            player.grab(item)
            player.drop()
            self.assertEqual(player.grabbed_obj, None)
            self.assertFalse(player.is_grabbing)

    def test_coord_with_grab(self):
        coords = [(-1,0), (1,1), (10, 100)]
        icoords = [(-1,1), (5,2), (9, 69)]
        for coord,icoord in zip(coords, icoords):
            player = reg.PlayerObject(
                obj_type="player",
                color=1,
                coord=coord,
                size=(1,1)
            )
            item = reg.PlayerObject(
                obj_type="item",
                color=1,
                coord=icoord,
                size=(2,5)
            )
            player.grab(item)
            self.assertEqual(player.coord, coord)

    def test_set_coord_with_grab(self):
        coords = [(-1,0), (1,1), (10, 100)]
        icoords = [(-1,1), (5,2), (9, 69)]
        dcoords = [(-11,-1), (15,12), (19, 169)]
        for coord,icoord,dcoord in zip(coords, icoords, dcoords):
            pcoord = coord_add(icoord, coord_diff(dcoord, coord))
            player = reg.PlayerObject(
                obj_type="player",
                color=1,
                coord=coord,
                size=(1,1)
            )
            item = reg.PlayerObject(
                obj_type="item",
                color=1,
                coord=icoord,
                size=(2,5)
            )
            player.grab(item)
            player.coord = dcoord
            self.assertEqual(player.player_coord, dcoord)
            self.assertEqual(player.coord, dcoord)
            self.assertEqual(item.coord, pcoord)

if __name__=="__main__":
    unittest.main()


