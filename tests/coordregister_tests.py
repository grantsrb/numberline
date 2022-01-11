import mathblocks.blocks.registry as mr
from mathblocks.blocks.grid import Grid
import numpy as np
import unittest

class CoordSet(unittest.TestCase):
    def test_all_objs_1obj(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        obj = mr.GameObject(
            coord=obj_coord,
            size=(1,1),
            color=1,
            obj_type="type1"
        )
        cr.add(obj)
        cs = mr.CoordSet(cr, obj_coord)
        self.assertEqual(obj, cs.all_objs.pop())

    def test_add_sametype(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        obj1 = mr.GameObject(
            coord=obj_coord,
            size=(1,1),
            color=1,
            obj_type="type1"
        )
        cr.add(obj1)
        obj2 = mr.GameObject(
            coord=obj_coord,
            size=(1,1),
            color=1,
            obj_type="type1"
        )
        cs = mr.CoordSet(cr, obj_coord)
        cs.add(obj2)
        self.assertEqual({obj1,obj2}, cs.all_objs)
        self.assertEqual({obj1,obj2}, cr.all_objs)

    def test_add_difftype(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        obj1 = mr.GameObject(
            coord=obj_coord,
            size=(1,1),
            color=1,
            obj_type="type1"
        )
        cr.add(obj1)
        obj2 = mr.GameObject(
            coord=(5,5),
            size=(1,1),
            color=1,
            obj_type="type2"
        )
        cs = mr.CoordSet(cr, obj_coord)
        cs.add(obj2)
        self.assertEqual({obj1,obj2}, cs.all_objs)
        self.assertEqual({obj1,obj2}, cr.all_objs)
        self.assertEqual(obj2.coord, obj_coord)

    def test_remove(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        obj1 = mr.GameObject(
            coord=obj_coord,
            size=(1,1),
            color=1,
            obj_type="type1"
        )
        obj2 = mr.GameObject(
            coord=obj_coord,
            size=(1,1),
            color=1,
            obj_type="type2"
        )
        cr.add(obj1)
        cr.add(obj2)
        cs = mr.CoordSet(cr, obj_coord)
        cs.remove(obj2)
        self.assertNotEqual({obj1,obj2}, cs.all_objs)
        self.assertEqual({obj1}, cr.all_objs)

    def test_all_objs_4obj(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        
        objs = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            )
        }

        for obj in objs:
            cr.add(obj)
        cs = mr.CoordSet(cr, obj_coord)
        self.assertEqual(objs, cs.all_objs)

    def test_all_objs_4obj_difflocs(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )

        obj_coord = (2,2)
        outlier = mr.GameObject(
            coord=(0,0),
            size=(1,1),
            color=1,
            obj_type="type1"
        )
        cr.add(outlier)
        objs = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(0,0),
                size=(3,3),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,1),
                size=(2,2),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(2,1),
                size=(1,2),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(2,1),
                size=(1,2),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,2),
                size=(2,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(1,2),
                size=(2,1),
                color=1,
                obj_type="type2"
            ),
        }

        for obj in objs:
            cr.add(obj)
        cs = mr.CoordSet(cr, obj_coord)
        self.assertEqual(objs, cs.all_objs)

    def test_diff_types(self):
        type1 = "type1"
        type2 = "type2"
        obj_types = {type1, type2}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )

        obj_coord = (2,2)
        type1s = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(0,0),
                size=(3,3),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(2,1),
                size=(1,2),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(1,2),
                size=(2,1),
                color=1,
                obj_type="type1"
            ),
        }
        type2s = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,1),
                size=(2,2),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(2,1),
                size=(1,2),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,2),
                size=(2,1),
                color=1,
                obj_type="type2"
            ),
        }

        for obj in type1s:
            cr.add(obj)
        for obj in type2s:
            cr.add(obj)
        cs = mr.CoordSet(cr, obj_coord)
        self.assertEqual(type1s, cs[type1])
        self.assertEqual(type2s, cs[type2])

class CoordRegisterTests(unittest.TestCase):
    def test_init(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        coords = Grid.all_coords((0,0), grid_shape)
        for coord in coords:
            self.assertTrue(coord in cr.hashmap)
            for ot in obj_types:
                self.assertTrue(ot in cr.hashmap[coord])

    def test_add(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (2,2)
        objs = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(0,0),
                size=(3,3),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,1),
                size=(2,2),
                color=1,
                obj_type="type2"
            ),
        }
        for obj in objs:
            cr.add(obj)
        self.assertEqual(cr.all_objs, objs)

    def test_remove(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (2,2)
        objs = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(0,0),
                size=(3,3),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,1),
                size=(2,2),
                color=1,
                obj_type="type2"
            ),
        }
        for obj in objs:
            cr.add(obj)
        remove_obj = objs.pop()
        cr.remove(remove_obj)
        self.assertEqual(cr.all_objs, objs)
        cr.remove(remove_obj) # test duplicatation of behavior
        self.assertEqual(cr.all_objs, objs)

    def test_add_with_new_coord(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (2,2)
        obj = mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            )
        cr.add(obj)
        self.assertEqual(cr.all_objs.pop(), obj)
        self.assertEqual(obj.coord, obj_coord)
        new_obj_coord = (3,3)
        cr.add(obj, new_obj_coord)
        self.assertEqual(cr.all_objs.pop(), obj)
        self.assertEqual(obj.coord, new_obj_coord)

    def test_duplicate_add(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (2,2)
        objs = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(0,0),
                size=(3,3),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,1),
                size=(2,2),
                color=1,
                obj_type="type2"
            ),
        }
        for obj in objs:
            cr.add(obj)
        for obj in objs:
            cr.add(obj)
        self.assertEqual(cr.all_objs, objs)

    def test_getitem(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (2,2)
        objs = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(0,0),
                size=(3,3),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,1),
                size=(2,2),
                color=1,
                obj_type="type2"
            ),
        }
        for obj in objs:
            cr.add(obj)
        coord_set = cr[obj_coord]
        self.assertEqual(type(coord_set), mr.CoordSet)
        self.assertEqual(coord_set.all_objs, objs)

    def test_move_obj(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (2,2)
        objs = {
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=(0,0),
                size=(3,3),
                color=1,
                obj_type="type1"
            ),
            mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type2"
            ),
            mr.GameObject(
                coord=(1,1),
                size=(2,2),
                color=1,
                obj_type="type2"
            ),
        }
        for obj in objs:
            cr.add(obj)
        moved_obj = objs.pop()
        new_coord = (obj_coord[0]+1, obj_coord[1]+1)
        cr.move_obj(moved_obj, new_coord)
        self.assertEqual(moved_obj.coord, new_coord)
        self.assertEqual(cr[new_coord].all_objs, {moved_obj})
        self.assertEqual(cr[obj_coord].all_objs, objs)

    def test_move_obj_with_size(self):
        obj_types = {"type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (1,1)
        new_coord = (3,3)
        obj1 = mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            )
        obj2 = mr.GameObject(
                coord=(0,0),
                size=(2,2),
                color=1,
                obj_type="type2"
            )
        cr.add(obj1)
        cr.add(obj2)
        all_init_coords1 = [(1,1)]
        for coord in all_init_coords1:
            self.assertTrue(obj1 in cr[coord])
        all_init_coords2 = [(0,0), (1,0), (0,1), (1,1)]
        for coord in all_init_coords2:
            self.assertTrue(obj2 in cr[coord])

        cr.move_obj(obj2, new_coord)
        for coord in all_init_coords1:
            self.assertTrue(obj1 in cr[coord])
        all_move_coords2 = [(3,3), (4,3), (3,4), (4,4)]
        for coord in all_move_coords2:
            self.assertTrue(obj2 in cr[coord])
            self.assertTrue(obj1 not in cr[coord])
        self.assertEqual(obj2.coord, new_coord)

    def test_move_player(self):
        obj_types = {"player", "type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        player_coord = (1,1)
        new_coord = (3,3)
        player = mr.Player(
                coord=player_coord,
                color=1,
            )
        obj = mr.GameObject(
                coord=obj_coord,
                size=(2,2),
                color=1,
                obj_type="type1"
            )
        cr.add(player)
        cr.add(obj)
        self.assertTrue(player in cr[player_coord])
        cr.move_player(player, new_coord)
        self.assertEqual(player.coord, new_coord)
        self.assertTrue(player in cr[new_coord])

    def test_move_player_holding(self):
        obj_types = {"player", "type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        player_coord = (1,1)
        new_coord = (3,3)
        player = mr.Player(
                coord=player_coord,
                color=1,
            )
        obj = mr.GameObject(
                coord=obj_coord,
                size=(2,2),
                color=1,
                obj_type="type1"
            )
        cr.add(player)
        cr.add(obj)
        player.grab(obj)
        cr.move_player(player, new_coord)
        self.assertEqual(player.coord, new_coord)
        self.assertTrue(player in cr[new_coord])
        old_coords = [(0,0), (1,0), (0,1), (1,1)]
        for coord in old_coords:
            self.assertFalse(obj in cr[coord])
        obj_coords = [(2,2), (2,3), (3,2), (3,3)]
        for coord in obj_coords:
            self.assertTrue(obj in cr[coord])

    def test_are_overlapping(self):
        obj_types = {"player", "type1", "type2"}
        grid_shape = (12,12)
        cr = mr.CoordRegister(
            obj_types=obj_types,
            grid_shape=grid_shape
        )
        obj_coord = (0,0)
        player_coord = (1,1)
        player = mr.Player(
                coord=player_coord,
                color=1,
            )
        obj = mr.GameObject(
                coord=obj_coord,
                size=(2,2),
                color=1,
                obj_type="type1"
            )
        obj2 = mr.GameObject(
                coord=obj_coord,
                size=(1,1),
                color=1,
                obj_type="type1"
            )
        cr.add(player)
        cr.add(obj)
        cr.add(obj2)
        self.assertTrue(cr.are_overlapping(player, obj))
        self.assertTrue(cr.are_overlapping(obj2, obj))
        self.assertFalse(cr.are_overlapping(obj2, player))



if __name__=="__main__":
    unittest.main()
