from mathblocks.blocks.grid import Grid
from mathblocks.blocks.constants import *
from mathblocks.blocks.utils import coord_diff, coord_add, nearest_obj, decompose, widest_width
from mathblocks.blocks.gameobjects import *
import math
import numpy as np

class Register:
    """
    The register tracks the coordinates of all objects within the game.
    The possible objects are:
      blocks - interactable objects that represent numerical values
      piles - the location for players to make and delete blocks
      players - the agents within the game
      dividers - a dividing line across the middle of the map to
        distinguish playable area from target area
      buttons - a button to press once the player thinks the task is
        finished
      operators - objects used to signify what mathematical operation
        should be performed to find the goal value of blocks
    
    The register has two data structures to track the items in the game.
    It has a set called all_objs that holds all of the GameObjects
    that are not dividers. It also has a CoordRegister that enables
    easy access to the objects located at particular coordinates within
    the game.

    The register provides methods for basic manipulations such as moving
    objects to specific coordinates, joining blocks into larger units,
    and creating and destroying objects.
    """
    @staticmethod
    def val2blocks(val):
        """
        Uses the argued value to create the appropriate number of blocks
        to represent that value. DOES NOT REGISTER THEM!!
        
        Args:
          val: int
            the value to be decomposed into blocks
        Return:
          blocks: set
              the blocks representing the value. the sum of the values
              of the blocks will be equivalent to the argued value
        """
        counts = decompose(val, BLOCK_VALS)

        blocks = set()
        for k in counts.keys():
            for i in range(counts[k]):
                blocks.add(
                    Block(
                        color=COLORS[BLOCK+str(k)],
                        val=k,
                        size=BLOCK_SIZES[k]
                    )
                )
        return blocks

    @staticmethod
    def make_eqn_blocks(left_val:int, right_val:int):
        """
        Creates the intial equation display. DOES NOT REGISTER THEM!!
        
        Args:
          left_val: int
            the value on the left side of the operator
          right_val: int
            the value on the right side of the operator
        Return:
          left_blocks: set
              the blocks representing the left value
          right_blocks: set
              the blocks representing the left value
        """
        left_blocks =  Register.val2blocks(left_val)
        right_blocks = Register.val2blocks(right_val)
        return left_blocks, right_blocks

    @staticmethod
    def apply_direction(coord: tuple, direction: int):
        """
        Changes a coord to reflect the applied direction. See the
        DIRECTIONS constant in `constants.py` to determine which value
        corresponds to which direction.

        Args:
            coord: tuple grid units (row, col)
            direction: int
                the movement direction. see the DIRECTIONS constant
        Returns:
            new_coord: tuple
                the updated coordinate
        """
        new_coord = tuple(coord)
        if direction == UP:
            new_coord = (coord[0]-1, coord[1])
        elif direction == RIGHT:
            new_coord = (coord[0], coord[1]+1)
        elif direction == DOWN:
            new_coord = (coord[0]+1, coord[1])
        elif direction == LEFT:
            new_coord = (coord[0], coord[1]-1)
        return new_coord


    def __init__(self, grid: Grid):
        """
        Args:
          grid: Grid
            the grid for the game
        """
        self.grid = grid
        self.eqn_row_offset = 2
        init_coord = (0,0)
        self.player = Player(
            color=COLORS[PLAYER],
            coord=init_coord
        )
        self.button = GameObject(obj_type=BUTTON, color=COLORS[BUTTON])
        self.blocks = set()
        self.piles = dict()
        for bv in BLOCK_VALS:
            key = PILE+str(bv)
            bc = COLORS[BLOCK+str(bv)]
            pile = Pile(
                color=COLORS[key],
                block_val=bv,
                block_size=BLOCK_SIZES[bv],
                block_color=bc,
                coord=init_coord,
                size=(1,1)
            )
            self.piles[key] = pile

        # All GameObjects used to the left and right of the operator in
        # the displayed equation
        self.left_eqn = set()
        self.right_eqn = set()
        self.operator = Operator(
            color=COLORS[OPERATOR],
            coord=init_coord,
            operation=ADD
        )
        self.all_objs = {
            self.player,
            *self.piles.values(),
            self.button,
            self.operator
        }
        self.coord_register = CoordRegister(OBJECT_TYPES, grid.shape)
        for obj in self.all_objs:
            self.coord_register.add(obj)
        self.button_event_registry = set()
        self.full_grid_event_registry = set()
        self._targ_val = None

    def __len__(self):
        return len(self.all_objs)

    @property
    def targ_val(self):
        if self._targ_val is None:
            self._targ_val = self.eqn_solution
        return self._targ_val

    @property
    def eqn_solution(self):
        """
        Directly solves the equation represented by the register.
        """
        left = 0
        for block in self.left_eqn:
            left += block.val 
        right = 0
        for block in self.right_eqn:
            right += block.val 
        if self.operator.operation == ADD: return left+right
        elif self.operator.operation == SUBTRACT: return left-right
        elif self.operator.operation == MULTIPLY: return left*right
        return None

    @property
    def n_blocks(self):
        return len(self.blocks)

    @property
    def block_counts(self):
        """
        Returns a dict of each type of block mapping to its count within
        the register
        
        Returns:
            counts: dict
                keys: str
                    the type of block (i.e. block10)
                vals: int
                    the number of instances of that block within the
                    register
        """
        counts = {bt: 0 for bt in BLOCK_TYPES}
        for block in self.blocks:
            counts[block.type] += 1
        return counts

    @property
    def block_sum(self):
        """
        Sum of all the values of the blocks in the game NOT INCLUDING
        THE BLOCKS THAT MAKE UP THE DISPLAYED EQUATION
        """
        s = 0
        for block in self.blocks:
            s += block.val
        return s

    def __contains__(self, obj):
        return obj in self.all_objs

    def __getitem__(self, coord):
        return self.coord_register[coord]

    def add_block(self, block, coord=None):
        """
        Adds a new block to the registers

        Args:
            block: Block
            coord: tuple of ints or None
                defaults to `block.coord` if None
        """
        if block in self.all_objs: return
        self.add_obj(block, coord)
        self.blocks.add(block)

    def add_obj(self, obj, coord=None):
        """
        Adds a new block to the registers

        Args:
            obj: GameObject
            coord: tuple of ints or None
                defaults to `obj.coord` if None
        """
        self.all_objs.add(obj)
        if coord is None: coord = obj.coord
        self.coord_register.add(obj, coord)

    def make_block(self, 
                   color: float,
                   val: int,
                   coord: tuple=(0,0),
                   size: tuple=(1,1)):
        """
        Args:
            color: float
              the color of the object
            val: int
              the representative number that each item created from this
              pile will represent.
            coord: tuple (row, col) in grid units
              the initial coordinate of the object
            size: tuple (n_row, n_col) in grid units
              the size of the rectangle representing the object.
        """
        new_block = Block(color=color, val=val, coord=coord, size=size)
        self.add_block(new_block, coord=coord)
        return new_block

    def make_eqn(self, left_val: int, operation: str, right_val:int):
        """
        Creates and registers the equation pieces, but does not
        arrange the pieces in space.

        Args:
          left_val: int
            the value on the left side of the operator
          operation: int
            the operator type
          right_val: int
            the value on the right side of the operator
        """
        self.clear_eqn()
        # Make new blocks to represent equation
        left =  Register.val2blocks(left_val)
        right = Register.val2blocks(right_val)
        # Add blocks to registers
        for l in left: self.add_obj(l, coord=(0,0))
        for r in right: self.add_obj(r, coord=(0,0))
        self.left_eqn, self.right_eqn = left, right

        # Place blocks and operator appropriately
        self.init_operator(operation)
        self.place_left_eqn()
        self.place_right_eqn()
        self._targ_val = self.eqn_solution

    def init_operator(self, operation):
        """
        Places the operator at a coordinate close to the center of the
        grid.
        """
        mid_col = self.grid.middle_col
        row = self.grid.middle_row + int(self.grid.shape[0]/8)
        coord = (row, mid_col)
        if self.grid.is_innonplay(coord):
            if self.operator is not None:self.delete_obj(self.operator)
            self.operator = Operator(
                color=COLORS[OPERATOR],
                coord=coord,
                operation=operation
            )
            self.add_obj(self.operator)

    def place_left_eqn(self, spacing=0):
        """
        Places the blocks contained within the left side of the eqn on
        to the grid.

        Args:
            spacing: int
                a space between each block
        """
        space = self.grid.shape[0]-self.grid.middle_row
        longest_block_len = BLOCK_SIZES[sorted(BLOCK_VALS)[-1]][0]
        row = self.grid.middle_row + int((space - longest_block_len)/2)
        endx = self.operator.coord[1]
        # Sorted blocks such that smallest are first
        blocks = sorted(list(self.left_eqn), key=lambda x: x.val)
        # Loop through blocks placing them further and further away
        # from operator.
        if len(blocks) > 0:
            col = endx
            for i,block in enumerate(blocks):
                col = col-spacing-block.size[1]
                assert col > 0
                coord = (row, col)
                self.move_obj(block, coord)

    def place_right_eqn(self, spacing=0):
        """
        Places the blocks contained within the right side of the eqn on
        to the grid.

        Args:
            spacing: int
                a space between each block
        """
        space = self.grid.shape[0]-self.grid.middle_row
        longest_block_len = BLOCK_SIZES[sorted(BLOCK_VALS)[-1]][0]
        row = self.grid.middle_row + int((space - longest_block_len)/2)
        startx = self.operator.coord[1]+self.operator.size[1]
        # Sorted blocks such that largest are first
        blocks = sorted(list(self.right_eqn), key=lambda x: -x.val)
        # Loop through blocks placing them further and further away
        # from operator.
        if len(blocks) > 0:
            col = startx+1
            self.move_obj(blocks[0], (row, col))
            for i in range(1, len(blocks)):
                col = col+blocks[i-1].size[1]+spacing
                assert col < self.grid.shape[1]
                self.move_obj(blocks[i], (row, col))

    def move_obj(self,
                 obj: GameObject,
                 coord: tuple=None,
                 size: tuple=None):
        """
        Takes an object and updates its coordinate to reflect the
        argued coord. Updates are reflected in coord_register and in
        the argued game object. Does not affect game object's
        prev_coord value but does update its coord value.

        If object does not move, this function returns False. This
        includes if the action is STAY and successfully completed.

        DOES NOT INVOKE attempt_merge EVEN IF A MERGE IS POSSIBLE!!!

        Args:
            obj: GameObject
                the game object that is being moved
            coord: tuple or None
                if this is argued and direction is None, the object
                is moved to this coord
            size: tuple or None
                the size of the object being moved. if None, defaults
                to `obj.size`
        Returns:
            did_move: bool
                if true, the move was legal and object was moved.
                If false, the move was either illegal or did not change
                the game object's coord value.
        """
        if coord == tuple(obj.coord):
            return False
        if size is None: size = obj.size
        if self.grid.is_inbounds(coord, size):
            self.coord_register.move_obj(obj, coord)
            return True
        return False

    def move_player(self, direction):
        """
        Takes a direction and updates the player's coordinate to
        reflect the applied direction. Updates are reflected in
        coord_register and in the player.

        If player does not move, this function returns False. This
        includes if the action is STAY and successfully completed.

        Args:
            direction: int
                the movement direction. See DIRECTIONS constant.
        Returns:
            did_move: bool
                if true, the move was legal and object was moved.
                If false, the move was either STAY and the game_object
                is updated. Or the move was illegal and the
                game_object does not change
        """
        # Determine new coordinate from the argued direction
        direction = direction % len(DIRECTIONS)
        coord = Register.apply_direction(self.player.coord, direction)
        # Determine size and coordinate of the moved entity (equal to
        # player if not holding an object, otherwise equal to held obj)
        size = self.player.size
        test_coord = coord
        if self.player.held_coord is not None:
            size = self.player.held_obj.size
            test_coord = self.player.subj_held_coord(coord)
        # If coordinate and size are inbounds, the object is moved
        if self.grid.is_playable(test_coord, size):
            self.coord_register.move_player(self.player, coord)
            return True
        return False

    def handle_grab(self):
        """
        Enables the player to grab the object it is standing on or 
        press a button or create a new object from a pile. If the agent
        is already holding an object, then handle_drop is invoked.

        If multiple objects are beneath the player the order of grab is
        as follows:

            - buttons
            - smallest blocks
            - largest blocks
            - piles

        If multiple objects of the same type all touch the same coord,
        the one with the closest `obj.coord` is grabbed.

        Returns:
            did_grab: bool
                if true, means that player successfully grabbed an obj.
                otherwise returns false.
        """
        player = self.player
        if player.is_holding: return self.handle_drop()

        objs = self.coord_register[player.coord]
        for key in GRAB_ORDER:
            if len(objs[key]) > 0:
                grab_obj = nearest_obj(player, objs[key])
                # Make new object if grabbed Pile
                if type(grab_obj) == Pile:
                    grab_obj = self.make_block(
                        color=grab_obj.block_color,
                        coord=player.coord,
                        val=grab_obj.block_val,
                        size=grab_obj.block_size
                    )
                player.grab(grab_obj)
                return True
        return False

    def handle_drop(self):
        """
        Enables the player to drop the item it is holding if it is
        holding an object.

        If the object is touching any pile it is
        deleted.

        If the object is touching the button, it is moved down
        the number of rows that is the size of the button.

        If the object is overlapping with enough other objects of its
        same type to merge into a larger block, this also occurs.

        Returns:
            did_drop: bool
        """
        player = self.player
        if not player.is_holding: return self.handle_grab()

        dropped_obj = player.drop()
        if self.coord_register.are_overlapping(dropped_obj, self.button):
            new_row = dropped_obj.coord[0]+self.button.size[0]
            new_coord = (new_row, dropped_obj.coord[1]) 
            self.move_obj(dropped_obj, new_coord)
        for pile in self.piles.values():
            if self.coord_register.are_overlapping(dropped_obj, pile):
                self.delete_obj(dropped_obj)
        self.attempt_merge(dropped_obj.coord)
        return True

    def handle_decomp(self):
        """
        Decomposes the object held by the agent into a collection of
        the next block size down. i.e. if the agent is holding a block
        of size 10, it will get broken into two blocks of size 5. If
        any of the new blocks is able to complete a merge with another
        set of blocks, this merge occurs.

        The player automatically drops the object it is holding even if
        it is not decomposed (i.e. player was holding the smallest
        block)

        Returns:
            did_decomp: bool
                true if decomposition occurred.
        """
        if not self.player.is_holding:
            return False
        obj = self.player.held_obj
        self.player.drop()
        return self.decompose_obj(obj)

    def decompose_obj(self, obj):
        """
        Decomposes the argued object into a collection of the next
        block size down. i.e. if the block is of size 10, it will get
        broken into two blocks of size 5. If any of the new blocks are
        able to complete a merge with another set of blocks, this
        merge occurs.

        Args:
            obj: Block
        Returns:
            did_decomp: bool
                true if decomposition occurred.
        """
        if not isinstance(obj, Block) or obj.val == BLOCK_VALS[0]:
            return False
        # A set of the start coordinates for the new blocks
        coords = DECOMP_COORDS[obj.val]
        # The values of the new blocks
        bvals = set(BLOCK_VALS)
        if obj.val in bvals: bvals.remove(obj.val)
        atoms = decompose(obj.val, bvals)
        self.delete_obj(obj)
        for val, count in atoms.items():
            for i in range(count):
                new_coord = coord_add(obj.coord, coords.pop())
                new_block = Block(
                    color=COLORS[BLOCK+str(val)],
                    val=val,
                    coord=new_coord,
                    size=BLOCK_SIZES[val]
                )
                self.add_block(new_block, coord=new_coord)
        return True

    def attempt_merge(self, coord):
        """
        If enough objects of the same type are located at the argued
        coordinate (the obj.coord values must all match!) to form a
        larger block, this function completes that action.

        Args:
            coord: tuple of ints
        Returns:
            did_merge: bool
                true if merge occurred
        """
        obj_dict = self.coord_register[coord]
        block_vals = sorted(BLOCK_VALS)
        did_merge = False
        filt_fxn = lambda x: x.coord==coord
        for i,bv in enumerate(block_vals[:-1]):
            btype = BLOCK+str(bv)
            blocks = list(filter(filt_fxn, obj_dict[btype]))
            bs = []
            for block in blocks:
                bs.append(block)
                val = len(bs)*bv
                if val == block_vals[i+1]:
                    self.merge(bs, block_vals[i+1])
                    did_merge = True
                    bs = []
        return did_merge

    def merge(self, blocks, new_val):
        """
        Merges the argued blocks to create a new block of new_val
        value, if possible.

        Args:
            blocks: list of Blocks
            new_val: int
                the new block will be of this value
        """
        if isinstance(blocks, set): blocks = list(blocks)
        bv = blocks[0].val
        coord = blocks[0].coord
        if len(blocks)*bv != new_val or new_val not in BLOCK_VALS:
            return False

        # Remove small Blocks
        for block in blocks:
            self.delete_obj(block)
        # Create new Block
        return self.make_block(
            color=COLORS[BLOCK+str(new_val)],
            val=new_val,
            coord=coord,
            size=BLOCK_SIZES[new_val]
        )

    def is_empty(self, coord, size=(1,1), ignores=set()):
        """
        A SPACE CAN BE CONSIDERED EMPTY EVEN IF THE PLAYER OCCUPIES IT!!

        Checks if the coordinates contained in the rectangle located
        at the argued coord are empty of GameObjects except for the
        player object. THE PLAYER OBJECT IS IGNORED!!!

        Args:
            coord: tuple in grid units (row, col)
            size: tuple in grid units (n_row, n_col)
            ignores: set of GameObjects
                gameobjects to ignore when considering if a space is
                empty
        Returns:
            bool
        """
        if not self.grid.is_inbounds(coord, size): return False
        coords = Grid.all_coords(coord, size)
        for c in coords:
            objs = self.coord_register[c].all_objs-ignores
            if len(objs) != 0 and self.player not in objs: return False
            elif len(objs) > 1: return False
        return True

    def is_playable(self, coord, size=(1,1)):
        """
        Determines if the coord is within playable bounds of the grid

        Args:
            coord: tuple in grid units (row, col)
            size: tuple in grid units (n_row, n_col)
        Returns:
            bool
        """
        return self.grid.is_playable(coord, size)

    def is_below_divider(self, coord):
        """
        Determines if the coord is within the space alotted for targets.
        If the grid is not divided, this means anywhere is fair game.
        If the grid is divided, then only the spaces below the middle
        line return true.
        """
        return self.grid.is_below_divider(coord)

    def is_overlapped(self, coord, size=(1,1)):
        """
        Checks if the argued coordinate has two or more GameObjects
        other than the player object. THE PLAYER OBJECT IS IGNORED!!!

        A SPACE IS NOT CONSIDERED TO OVERLAP IF THE PLAYER OCCUPIES IT
        WITH ANOTHER OBJECT!! THE PLAYER DOES NOT COUNT IN THIS
        FUNCTION!!

        Args:
            coord: tuple in grid units (row, col)
            size: tuple in grid units (nrow, ncol)
        Returns:
            is_overlapping: bool
                if true, multiple GameObjects other than the player
                object reside in this space
        """
        coord = tuple(coord)
        if not self.is_playable(coord): return False
        coords = Grid.all_coords(coord, size)
        for c in coords:
            objs = self.coord_register[c]
            if len(objs) <= 1: return False
            elif self.player in objs and len(objs) <= 2: return False
        return True

    def find_space(self, coord, size=(1,1)):
        """
        Searches around the argued coord for a coordinate that is
        either empty or only contains a player game object. Only
        spaces that are within the playable boundaries are considered.

        The order of the search is the pixels connected to the argued
        coordinate starting in the upper left connected pixel moving
        across the top to the right, then lower left pixel moving
        across the bottom to the right, then leftmost pixels in
        between the top and bottom moving from top to bottom, then the
        rightmost pixels in between the top and bottom. If none of
        these spaces are free, the search repeats one more layer
        outward.

        Args:
            coord: tuple in grid units (row, col)
                this is the root of the breadth first search. It is
                not included in the search.
        Returns:
            free_coord: tuple
                the nearest coordinate that is empty or only contains
                a player object.
        """
        def test_loc(loc):
            """
            loc: tuple coordinate in grid units (row, col)
            """
            return (
                self.is_playable(loc,size) and self.is_empty(loc,size)
            )
        row,col = coord
        layer = 0
        while layer < max(*self.grid.shape):
            layer += 1
            min_row = row - layer
            min_col = col - layer
            max_row = row + layer
            max_col = col + layer
            for i in range(max_col-min_col+1):
                loc = (min_row, min_col+i)
                if test_loc(loc): return loc
                loc = (max_row, min_col+i)
                if test_loc(loc): return loc
            for i in range(1,max_row-min_row):
                loc = (min_row+i, min_col)
                if test_loc(loc): return loc
                loc = (min_row+i, max_col)
                if test_loc(loc): return loc
        self.raise_full_grid_event()
        return None

    def delete_obj(self, obj, draw=False):
        """
        Deletes the object from the registries and the grid

        Args:
            obj: GameObject
                the gameobject to be deleted
        """
        # Doing this here for efficiency benefits
        if draw:
            self.grid.draw(
                obj.prev_coord,
                size=obj.size,
                color=-obj.color,
                add_color=True
            )
        self.coord_register.remove(obj)
        if obj in self.all_objs: self.all_objs.remove(obj)
        if self.player.held_obj == obj: self.player.drop()
        if type(obj) == Block:
            if obj in self.blocks: self.blocks.remove(obj)
            elif obj in self.left_eqn: self.left_eqn.remove(obj)
            elif obj in self.right_eqn: self.right_eqn.remove(obj)
        elif obj == self.player:
            del self.player
            self.player = None
        elif obj == self.button:
            del self.button
            self.button = None
        elif type(obj) == Pile:
            if obj.type in self.piles: del self.piles[obj.type]
        elif type(obj) == Operator:
            del self.operator
            self.operator = None
        else: del obj

    def clear_blocks(self):
        """
        Deletes all items from the registers.
        """
        reg = {*self.all_objs}
        for obj in reg:
            if type(obj) == Block: self.delete_obj(obj)

    def clear_eqn(self):
        """
        Deletes all blocks and the operator from the equation.
        """
        self.delete_obj(self.operator)
        for b in self.left_eqn:
            self.delete_obj(b)
        for b in self.right_eqn:
            self.delete_obj(b)

    def draw_register(self):
        """
        This function updates the grid with the current state of the
        registers.

        Each GameObject's prev_coord is updated to the value of coord.

        The draw process wipes the grid to the default value, then for
        each coordinate all GameObjects at that coordinate sum their
        colors together which is then drawn to the grid at that coord.
        """
        # clears all information on the grid but maintains intial
        # ndarray reference self.grid._grid.
        self.grid.clear(remove_divider=False)
        for obj in self.all_objs:
            obj.prev_coord = obj.coord
            self.grid.draw(
                coord=obj.coord,
                size=obj.size,
                color=obj.color,
                add_color=True
            )

    def draw_register_changes(self):
        """
        This function only updates the grid with changes made to the
        registered game objects. It searches for differences in 
        a GameObject's prev_coord and coord and updates the grid to
        reflect these changes.

        Each GameObject's prev_coord is updated to the value of coord.
        """
        for obj in self.all_objs:
            if obj.prev_coord != obj.coord:
                # Delete previous value
                self.grid.draw(
                    coord=obj.prev_coord,
                    color=-obj.color,
                    size=obj.size,
                    add_color=True
                )
                # Add new value
                self.grid_draw(
                    coord=obj.coord,
                    color=obj.color,
                    size=obj.size,
                    add_color=True
                )
                obj.prev_coord = obj.coord

    def set_nonblocks(self):
        """
        Sets the button, player, and piles along the top row. Does so
        such that all piles are located next to each other and the
        ending button and player are randomly started along the top row.
        """
        self.player.drop()
        avail_cols = self.init_piles()
        shuff = list(avail_cols)
        np.random.shuffle(shuff)
        self.move_obj(self.player, (0, shuff[0]))
        self.move_obj(self.button, (0, shuff[1]))

    def init_piles(self):
        """
        Sets the initial locations of the piles. Each pile is located
        at row 0 beginning at a random column.

        Returns:
            avail_cols: set of ints
                the remaining available columns
        """
        # Subtract widest block size from potential start columns
        width = widest_width(BLOCK_SIZES)
        n_cols = self.grid.shape[1]-width
        # Determine how much space the columns will take
        pile_space = 0
        for pile in self.piles.values():
            pile_space += pile.size[1]
        # Pick random initial start column
        start = np.random.randint(0, n_cols-pile_space)
        # Place piles along the top row from the start col
        takens = set()
        offset = 0
        for bv in BLOCK_VALS:
            coord = (0, start+offset)
            pile = self.piles[PILE+str(bv)]
            self.move_obj(pile, coord)
            offset += pile.size[1]
            for i in range(coord[1], coord[1]+pile.size[1]):
                takens.add(i)
        return {*np.arange(n_cols, dtype=np.int)}-takens

    def avail_coord_on_row(self, obj, row, min_col=0):
        """
        Finds the next available coordinate along the row that will
        allow the object to be dropped without overlapping with any
        other gameobjects. If no coord can be found, returns None

        Args:
            obj: GameObject
            row: int
                the row to search along
            min_col: int
                the col to start the search from
        Returns:
            coord: tuple of ints or None
                the next available space starting from min_col that
                the object can exist in without overlapping with any
                objects other than the player.
        """
        col = min_col
        while col < self.grid.shape[1]:
            coord = (row, col)
            if self.is_empty(coord, obj.size, ignores={obj}):
                return coord
            col += 1
        return None

class CoordRegister:
    """
    This class assists in tracking what GameObjects are located at each
    coordinate. The class holds a 2d array for each GameObject type.
    For each GameObject of within a type, an integer is added to all
    coordinates that are occupied by that GameObject.

    Use the function `move_obj(obj, new_coord)` to update the internal
    representation.
    """
    def __init__(self, obj_types, grid_shape):
        """
        Args:
            obj_types: set of str
                each GameObject type that should be tracked
            grid_shape: tuple (n_row, n_col)
                the shape of the grid in grid units "grid.shape"
        Members:
            hashmap: dict
                the hashmap is a dict that maps coordinates to dicts
                that map from object type strings to sets of the
                corresponding objects that are touching that location.
        """
        self.hashmap = dict()
        for row in range(grid_shape[0]):
            for col in range(grid_shape[1]):
                coord = (row,col)
                self.hashmap[coord] = {ot: set() for ot in obj_types}

    @property
    def all_objs(self):
        """
        Returns:
            objs: set of GameObjects
                all objects in the coord register
        """
        objs = set()
        for coord in self.hashmap.keys():
            for otype in self.hashmap[coord].keys():
                objs = {*objs, *self.hashmap[coord][otype]}
        return objs

    def __contains__(self, obj):
        """
        Returns:
            contained: bool
                true if object is somewhere in the coord register
        """
        return obj in self.all_objs

    def __getitem__(self, coord):
        """
        Args:
            coord: tuple of ints (Row, Col)
                the coordinate location in grid units
        Returns:
            objs: CoordSet
                a special datastructure that contains all objects that
                are partially touching the argued location
        """
        return CoordSet(self, tuple(coord))

    def add(self, obj, coord=None):
        """
        Adds a new object to the hashmap

        Args:
            obj: GameObject
            coord: tuple of ints (row, col) or None
                if None, obj.coord is used instead
        """
        if coord is None: coord = obj.coord
        if obj in self[obj.coord] or obj in self.all_objs:
            self.move_obj(obj, coord)
        else:
            obj.coord = coord
            coords = Grid.all_coords(obj.coord, obj.size)
            for c in coords:
                if obj.type in self.hashmap[c]:
                    self.hashmap[c][obj.type].add(obj)
                else:
                    self.hashmap[c][obj.type] = {obj}

    def remove(self, obj):
        """
        Removes an object from the hashmap

        Args:
            obj: GameObject
        """
        if obj not in self.all_objs: return
        coords = Grid.all_coords(obj.coord, obj.size)
        for c in coords:
            if obj in self.hashmap[c][obj.type]:
                self.hashmap[c][obj.type].remove(obj)

    def move_obj(self, obj, new_coord):
        """
        Moves the GameObject from its current coordinate to the argued
        new coord. Assumes the GameObject's current coordinate is
        represented by its `coord` member variable. This function
        updates the object's "coord" value to the new_coord.

        Args:
            obj: GameObject
            new_coord: tuple of ints (row, col)
                the new coordinate in grid units
        """
        # Collect coordinate sets
        old_coords = Grid.all_coords(obj.coord, obj.size)
        new_coords = Grid.all_coords(new_coord, obj.size)
        # The coordinates to delete the object from
        del_coords = old_coords-new_coords
        # The coordinates to add the object to
        add_coords = new_coords-old_coords

        for coord in del_coords:
            if obj in self.hashmap[coord][obj.type]:
                self.hashmap[coord][obj.type].remove(obj)
        for coord in add_coords:
            self.hashmap[coord][obj.type].add(obj)
        obj.coord = new_coord

    def move_player(self, player, new_coord):
        """
        Moves the player from its current coordinate to the argued
        new coord. Assumes the player's current coordinate is
        represented by its `coord` member variable. This function
        updates the object's "coord" value to the new_coord and moves
        any held objects with the player.

        Args:
            obj: GameObject
            new_coord: tuple of ints (row, col)
                the new coordinate in grid units
        """
        if player.is_holding:
            new_held_coord = player.subj_held_coord(new_coord)
            self.move_obj(player.held_obj, new_held_coord)
        self.move_obj(player, new_coord)

    def are_overlapping(self, obj1, obj2):
        """
        Determines if the two argued objects are overlapping at all on
        the grid.

        Args:
            obj1: GameObject
            obj2: GameObject
        Returns:
            overlapping: bool
                true if any part of the objects overlaps
        """
        coords1 = Grid.all_coords(obj1.coord, obj1.size)
        coords2 = Grid.all_coords(obj2.coord, obj2.size)
        overlaps = coords1.intersection(coords2)
        return len(overlaps) > 0

class CoordSet:
    """
    Acts as a helper class to the CoordRegister. This class is returned
    when the CoordRegister is indexed. It enables the user to add and
    remove blocks from the CoordRegister at this coordinate using this
    class' API
    """
    def __init__(self, coord_register, coord):
        """
        Args:
            coord_register: CoordRegister
            coord: tuple of ints (row, col)
                the coordinate that the user is interested in
        """
        self.cregister = coord_register
        self.coord = coord

    @property
    def all_objs(self):
        """
        Returns a set of all objects at this location
        """
        d = self.cregister.hashmap[self.coord]
        objs = set()
        for k in d.keys():
            objs = {*objs, *d[k]}
        return objs

    def __contains__(self, obj):
        d = self.cregister.hashmap[self.coord]
        if obj.type in d:
            return obj in d[obj.type]
        return False

    def __iter__(self):
        return iter(self.all_objs)

    def __getitem__(self, obj_type):
        """
        Returns a set of the objects at this coordinate of the argued
        type. Returns an empty set if the obj_type does not exist.

        Args:
            obj_type: str
        Returns:
            objs: set
                a set of the all the objects of the argued type at this
                coordinate.
        """
        if obj_type in self.cregister.hashmap[self.coord]:
            return self.cregister.hashmap[self.coord][obj_type]
        return set()

    def __len__(self):
        return len(self.all_objs)

    def add(self, obj):
        """
        This function is used to quickly add blocks to the CoordRegister
        at the coordinate that corresponds to this CoordSet

        Args:
            obj: GameObject
        """
        self.cregister.add(obj, self.coord)

    def remove(self, obj):
        """
        This function is used to quickly remove GameObjects from the
        CoordRegister entirely.

        Args:
            obj: GameObject
        """
        self.cregister.remove(obj)

