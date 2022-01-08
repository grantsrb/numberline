from mathblocks.blocks.grid import Grid
from mathblocks.blocks.constants import *
from mathblocks.blocks.utils import coord_diff, coord_add, nearest_obj
import math
import numpy as np

class GameObject:
    """
    The GameObject class is the main class for tracking what types of
    objects are on the grid. It contains the current coordinate and
    type of object.
    """
    def __init__(self,
                 obj_type: str,
                 color: float,
                 coord: tuple=(0,0),
                 size: tuple=(1,1)):
        """
        obj_type: str
          the type of object. see OBJECT_TYPES for a list of available
          types.
        color: float
          the color of the object
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        size: tuple (n_row, n_col) in grid units
          the size of the rectangle representing the object.
        """
        self._obj_type = obj_type
        self._color = color
        self.coord = coord
        self._size = size
        # used to track changes for drawing to grid
        self.prev_coord = (-math.inf, -math.inf)

    def move_to(self, coord):
        """
        Moves the object to the argued coordinate.
        """
        self.prev_coord = self.coord
        self.coord = coord

    @property
    def type(self):
        return self._obj_type

    @property
    def color(self):
        return self._color

    @property
    def size(self):
        return self._size

    def __str__(self):
        return self.type

class Player(GameObject):
    """
    The player object has special abilities to hold objects. While a
    player object is holding another object, updates to the player's
    coordinates will affect the object it is holding as well.
    """
    def __init__(self,
                 color: float,
                 coord: tuple=(0,0),
                 size: tuple=(1,1)):
        """
        color: float
          the color of the object
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        size: tuple (n_row, n_col) in grid units
          the size of the rectangle representing the object.
        """
        super().__init__(
            obj_type=PLAYER,
            color=color,
            coord=coord,
            size=size
        )
        self.held_obj = None

    def grab(self, obj):
        """
        Assists in grabbing a GameObject.

        Args:
            obj: GameObject
        """
        self.held_obj = obj

    def drop(self):
        """
        Assists in dropping a GameObject.
        """
        obj = self.held_obj
        self.held_obj = None
        return obj

    @property
    def is_holding(self):
        return self.held_obj is not None

    @property
    def held_coord(self):
        """
        Returns the coordinate of the held object if the player is
        holding an object.

        Returns:
            coord: tuple of ints or None
        """
        if self.is_holding: return self.held_obj.coord
        return None

    def subj_held_coord(self, subj_player_coord):
        """
        Returns what the coordinate of the held object would be if the
        player were to move to the argued coordinate.

        subj stands for subjunctive.

        Args:
            subj_player_coord: tuple of ints (row,col)
                the would be coordinate of the player. this function
                will determine what the held object's coordinate would
                be if the player were moved to the subj_player_coord
        Returns:
            coord: tuple of ints or None
                returns the coordinate where the held object would be
                if the player were to move to the argued coorindate. 
                returns None if the player is not holding an object.
        """
        if self.held_coord is None: return None
        vector = coord_diff(self.coord, subj_player_coord)
        return coord_add(vector, self.held_coord)

class Pile(GameObject):
    """
    Piles are a special type of gameobject that allow creation of a
    new item of a particular size, color, and representative quantity.
    The Pile class holds the information for all new items created from
    itself.
    """
    def __init__(self, 
                 color: float,
                 block_val: int,
                 block_size: tuple,
                 block_color: float,
                 coord: tuple=(0,0),
                 size: tuple=(1,1)):
        """
        color: float
          the color of the object
        block_val: int
          the representative number that each item created from this
          pile will represent.
        block_size: int
          the size of each block created from this pile
        color: float
          the color of each item created from this pile
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        size: tuple (n_row, n_col) in grid units
          the size of the rectangle representing the object.
        """
        super().__init__(
            obj_type=PILE+str(block_val),
            color=color,
            coord=coord,
            size=size
        )
        self.block_val = block_val
        self.block_size = block_size
        self.block_color = block_color

class Operator(GameObject):
    """
    Operators are a special type of gameobject that represent the
    mathematical operation being performed in the displayed equation.
    """
    @staticmethod
    def operation2size(operation):
        """
        Takes an operation and returns the size that the operator
        should be. Operations are distinguished by the shape of the
        operator object.

        Args:
            operation: str
        Returns:
            size: tuple (n_row,n_col)
        """
        if operation == ADD:
            return (2,1)
        elif operation == SUBTRACT:
            return (1,2)
        elif operation == MULTIPLY:
            return (1,1)
        else:
            raise NotImplemented

    def __init__(self, 
                 color: float,
                 operation: str=ADD,
                 coord: tuple=(0,0)):
        """
        color: float
          the color of the object
        operation: str
            the current operation that this operator represents
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        """
        self.operation = operation
        size = Operator.operation2size(self.operation)
        super().__init__(
            obj_type=OPERATOR,
            color=color,
            coord=coord,
            size=size
        )

class Block(GameObject):
    """
    Blocks are the building block :) of the game. Each block represents
    a quantity. They can be stacked to build bigger blocks.
    """
    def __init__(self,
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
        self.val = val
        super().__init__(
            obj_type=BLOCK+str(self.val),
            color=color,
            coord=coord,
            size=size
        )

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


    TODO: move this to Controller logic !!!!!!!!!!!!!!!!!!!!!!!!
    If the player was carrying an object and stepped onto another
    object, the game is handled as follows. While the player
    continues to grab, all objects and the player remain overlayn.
    If the player releases the grab button while an object is on
    top of another object, one of 2 things can happen. If the 
    underlying object is a pile, the item is returned to the pile.
    If the underlying object is an item, the previously carried
    item is placed in the nearest empty location from its current
    coord.

    The order of the search is the pixels connected to the argued
    coordinate starting in the upper left connected pixel moving
    across the top to the right, then lower left pixel moving
    across the bottom to the right, then leftmost pixels in
    between the top and bottom moving from top to bottom, then the
    rightmost pixels in between the top and bottom. If none of
    these spaces are free, the search repeats one more layer
    outward.
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
    def apply_direction(coord: tuple, direction: int):
        """
        Changes a coord to reflect the applied direction

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
        init_coord = (0,0)
        self.player = Player(
            color=COLORS[PLAYER],
            coord=init_coord,
            size=(1,1)
        )
        self.button = GameObject(obj_type=BUTTON, color=COLORS[BUTTON])
        self.blocks = set()
        self.piles = dict()
        for bv, bs in zip(BLOCK_VALS, BLOCK_SIZES):
            key = PILE+str(bv)
            bc = COLORS[BLOCK+str(bv)]
            pile = Pile(
                color=COLORS[key],
                block_val=bv,
                block_size=bs,
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
            size=(1,1),
            coord=init_coord
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

    @property
    def targ_val(self):
        return self._targ_val

    @property
    def n_blocks(self):
        return len(self.blocks)

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

    def make_eqn_blocks(self, left_val:int, right_val:int):
        """
        Creates the intial equation display. DOES NOT REGISTER THEM!!
        
        Args:
          left_val: int
            the value on the left side of the operator
          right_val: int
            the value on the right side of the operator
        Return:
          left_blocks: list
              the blocks representing the left value
          right_blocks: list
              the blocks representing the left value
        """
        left_blocks =  Register.val2blocks(left_val)
        right_blocks = Register.val2blocks(right_val)
        return left_blocks, right_blocks

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
        raise NotImplemented

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
        size = player.size
        test_coord = player.coord
        if player.held_coord is not None:
            size = player.held_obj.size
            test_coord = player.subj_held_coord(coord)
        # If coordinate and size are inbounds, the object is moved
        if self.grid.is_playable(test_coord, size):
            self.coord_register.move_obj(obj, coord)
            return True
        return False

    def handle_grab(self):
        """
        Enables the player to grab the object it is standing on or 
        press a button or create a new object from a pile. 

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
        if player.is_holding: return False

        objs = self.coord_register[player.coord]
        for key in GRAB_ORDER:
            if len(objs[key]) > 0:
                grab_obj = nearest_obj(player, objs)
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
        holding an object. If the object is touching any pile it is
        deleted. If the object is touching the button, it is moved down
        the number of rows that is the size of the button. If the object
        is overlapping with enough other objects of its same type to
        merge into a larger block, this also occurs.

        Returns:
            did_drop: bool
        """
        player = self.player
        if not player.is_holding: return False

        dropped_obj = player.drop()
        for pile in self.piles:
            if self.coord_register.are_overlapping(dropped_obj, pile)
                self.delete_obj(dropped_obj)
        if self.coord_register.are_overlapping(dropped_obj, self.button):
            new_row = dropped_obj.coord[0]+self.button.size[0]
            new_coord = (new_row, dropped_obj.coord[1]) 
            self.move_obj(dropped_obj, new_coord)
        self.attempt_merge(dropped_obj.coord)
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
                    break
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
        bv = blocks[0].val
        coord = blocks[0].coord
        assert len(blocks)*bv == new_val

        # Remove small Blocks
        for block in blocks:
            self.delete_obj(block)
        # Create new Block
        self.make_block(
            color=COLORS[BLOCK+str(new_val)],
            val=new_val,
            coord=coord,
            size=BLOCK_SIZES[new_val]
        )

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

    def add_block(self, block, coord=None):
        """
        Adds a new block to the registers

        Args:
            block: Block
            coord: tuple of ints or None
                defaults to `block.coord` if None
        """
        if block in self.all_objs: return
        self.all_objs.add(block)
        self.coord_register.add(block)
        self.blocks.add(block)

    def handle_decomp(self):
        """
        Decomposes the object held by the agent into a collection of
        the next block size down. i.e. if the agent is holding a block
        of size 10, it will get broken into two blocks of size 5. If
        any of the new blocks is able to complete a merge with another
        set of blocks, this merge occurs.

        Returns:
            did_decomp: bool
                true if decomposition occurred.
        """
        player = self.player
        if not player.is_holding or obj.val == sorted(BLOCK_VALS)[0]:
            return False
        obj = player.held_obj
        # A set of the start coordinates for the new blocks
        coords = DECOMP_COORDS[obj.val]
        # The values of the new blocks
        atoms = decompose(obj.val, BLOCK_VALS)
        for val, count in atoms.items():
            for i in range(count):
                new_coord = coord_add(obj.coord, coords.pop())
                new_block = Block(
                    color=COLORS[BLOCK+str(val)],
                    val=val,
                    coord=new_coord,
                    size=BLOCK_SIZES[new_val]
                )
                self.add_block(new_block, coord=new_coord)
        return True

    def is_empty(self, coord, size=(1,1)):
        """
        A SPACE CAN BE CONSIDERED EMPTY EVEN IF THE PLAYER OCCUPIES IT!!

        Checks if the coordinates contained in the rectangle located
        at the argued coord are empty of GameObjects except for the
        player object. THE PLAYER OBJECT IS IGNORED!!!

        Args:
            coord: tuple in grid units (row, col)
            size: tuple in grid units (n_row, n_col)
        Returns:
            bool
        """
        if not self.grid.is_inbounds(coord, size): return False
        coords = Grid.all_coords(coord, size)
        for c in coords:
            objs = self.coord_register[c]
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

    def delete_obj(self, obj):
        """
        Deletes the object from the registries and the grid

        Args:
            obj: GameObject
                the gameobject to be deleted
        """
        # Doing this here for efficiency benefits
        self.grid.draw(
            obj.prev_coord,
            size=obj.size,
            color=-obj.color,
            add_color=True
        )
        self.coord_register.remove(obj)
        self.all_objs.remove(obj)
        if player.held_obj == obj: player.drop()
        if type(obj) == BLOCK: self.blocks.remove(obj)
        elif obj == self.player: del self.player
        elif obj == self.button: del self.button
        elif type(obj) == Pile: self.piles.remove(obj)
        elif type(obj) == Operator: del self.operator
        else: del obj

    def delete_blocks(self):
        """
        Deletes all items from the registers.
        """
        reg = {*self.all_objs}
        for obj in reg:
            if type(obj) == Block: self.delete_obj(obj)

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


    ## Probably don't want a reset within this class. The reset should
    ## be handled by the controller. This way we can easily choose
    ## if we want to display a visual representation of the eqn or not
    def reset(self, left_val: int, operation: str, right_val:int):
        """
        Resets the grid and draws the register to the grid

        Args:
          left_val: int
            the value on the left side of the operator
          operation: int
            the operator type
          right_val: int
            the value on the right side of the operator
        """
        self.delete_items()
        self.make_eqn(targ_val)
        self.grid.reset() # makes a fresh grid
        self.draw_register()

    # TODO: finish make_eqn func on 402
    # make a system for grabbing
    # make system for moving objects restricted to within bounds
    # make system for adding and deleting objects
    # make a system for merging blocks




    def step(self, direction: int, grab: int):
        """
        Step takes two actions and moves the player and any items
        appropriately.

        If the player was carrying an object and stepped onto another
        object, the game is handled as follows. While the player
        continues to grab, all objects and the player remain overlayn.
        If the player releases the grab button while an object is on
        top of another object, one of 2 things can happen. If the 
        underlying object is a pile, the item is returned to the pile.
        If the underlying object is an item, the previously carried
        item is placed in the nearest empty location in this order.
        Up, right, down, left. If none are available a search algorithm
        is performed spiraling outward from the center. i.e. up 2, up 2
        right 1, up 2 right 2, up 1 right 2, right 2, etc.

        Args:
          direction: int [0, 1, 2, 3, 4]
            Check DIRECTIONS to ensure these values haven't changed
                0: no movement
                1: move up (lower row unit)
                2: move right (higher column unit)
                3: move down (higher row unit)
                4: move left (lower column unit)
          grab: int [0,1]
            grab is an action to enable the agent to carry items around
            the grid. when a player is on top of an item, they can grab
            the item and carry it with them as they move. If the player
            is on top of a pile, a new item is created and carried with
            them to the next square.
        
            0: quit grabbing item
            1: grab item. item will follow player to whichever square
              they move to.
        """
        # If did_move is false, the move was either STAY or illegal.
        # Either way, the player object's prev_coord will be updated
        # to reflect what its coord variable was before entering the
        # move object function
        did_move = self.move_player(direction)

        if grab == 0:
            # must check for overlapping objects and handle
            # appropriately
            event = self.handle_drop(self.player)
        else:
            # if player was grabbing, create new item if previous
            # location was a pile, raise button press event if previous
            # location was a button, and carry item to current
            # coordinate if previous location was an item
            event = self.handle_grab(self.player)
        # Draws all registered objects to the grid and updates their
        # previous coord to their current coord
        self.draw_register()
        return event


    def rand_targ_placement(self):
        """
        Places the targets randomly on the grid.
        """
        coords = {(0,0)}
        if self.grid.is_divided: low = self.grid.middle_row+1
        else: low = 0
        high = self.grid.shape[0]
        assert self.n_targs < (high-low)*self.grid.shape[1]
        for targ in self.targs:
            coord = (0,0)
            while not self.is_empty(coord) or coord in coords:
                row = np.random.randint(low, high)
                col = np.random.randint(0, self.grid.shape[1])
                coord = (row, col)
            coords.add(coord)
            self.move_object(targ, coord=coord)

    def even_targ_spacing(self):
        """
        Evenly spaces the targets by a random amount and places them
        along a random row (below the divider) beginning at a random
        column.
        """
        row = np.random.randint(
            self.grid.middle_row+1,
            self.grid.shape[0]
        )
        avail_col_space = self.grid.shape[1] - self.n_targs
        max_spacing = avail_col_space//max(self.n_targs-1, 1)
        space_between = 0
        if max_spacing > 0:
            space_between = np.random.randint(0,max_spacing)
        start_col = 0
        taken_space = self.n_targs + space_between*(self.n_targs-1)
        space_left = self.grid.shape[1]-taken_space
        start_col = np.random.randint(0,space_left+1)
        for i,targ in enumerate(self._targs):
            col = start_col + i*(space_between+1)
            coord = (row, col)
            self.move_object(targ, coord=coord)

    def uneven_targ_spacing(self, max_spacing=5):
        """
        Unevenly spaces the targets by a random amount and places them
        along a single random row (below the divider).

        Args:
            max_spacing: int
                the maximum spacing that can occur between two targets.
                (inclusive)
        """
        row = np.random.randint(
            self.grid.middle_row+1,
            self.grid.shape[0]
        )
        avail_col_space = self.grid.shape[1] - self.n_targs
        spacings = []
        for i in range(self.n_targs-1):
            if avail_col_space == 0:
                spacings.append(0)
            else:
                lim = min(max_spacing+1, avail_col_space)
                spacing = np.random.randint(0,lim)
                spacings.append(spacing)
                avail_col_space -= spacing
        spacings = np.random.permutation(spacings)
        start_col = np.random.randint(0,avail_col_space+1)

        for i,targ in enumerate(self._targs):
            if i > 0:
                start_col = start_col + spacings[i-1] + 1
            coord = (row, start_col)
            self.move_object(targ, coord=coord)

    def vertical_targ_spacing(self):
        """
        Evenly spaces the targets by a random amount and places them
        along a random column (below the divider) beginning at a random
        row.
        """
        col = np.random.randint(
            0,
            self.grid.shape[1]
        )
        if self.grid.is_divided:
            space = self.grid.shape[0] - self.grid.middle_row - 1
            start_row = self.grid.middle_row + 1
        else:
            space = self.grid.shape[0]
            start_row = 0
        avail_row_space = space - self.n_targs
        max_spacing = avail_row_space//max(self.n_targs-1, 1)
        space_between = 0
        if max_spacing > 0:
            space_between = np.random.randint(0,max_spacing)

        taken_space = self.n_targs + space_between*(self.n_targs-1)
        space_avail = space-taken_space
        start_row = start_row + np.random.randint(0,space_avail+1)
        for i,targ in enumerate(self._targs):
            row = start_row + i*(space_between+1)
            coord = (row, col)
            self.move_object(targ, coord=coord)

    def even_line_match(self):
        """
        Initialization function for the line match game A.

        The agent must align a block along the column of each
        of the target objects
        """
        # each is randomly placed in the top row of the grid
        self.rand_pile_button_player() 
        self.even_targ_spacing()
        self.draw_register()

    def cluster_match(self):
        """
        Intialization function for the Cluster Match game B.

        The agent must match the number of target objects without
        aligning them.
        """
        self.rand_pile_button_player() 
        self.rand_targ_placement()
        self.draw_register()

    def orthogonal_line_match(self):
        """
        Initialization function for the orthogonal line match game C.

        The agent must evenly space a block for each target along a
        single column.
        """
        self.rand_pile_button_player()
        self.vertical_targ_spacing()
        self.draw_register()

    def uneven_line_match(self):
        """
        Initialization function for the uneven line match game D.

        The agent must align a block along the column of each
        of the target objects
        """
        self.rand_pile_button_player()
        self.uneven_targ_spacing()
        self.draw_register()

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
        self.all_objs = set()
        self.hashmap = dict()
        for row in range(grid_shape[0]):
            for col in range(grid_shape[1]):
                coord = (row,col)
                self.hashmap[coord] = {ot: set() for ot in obj_types}

    def __getitem__(self, coord):
        """
        Args:
            coord: tuple of ints (Row, Col)
                the coordinate location in grid units
        Returns:
            objs: set of GameObjects
                all objects that are partially touching that location
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
            self.all_objs.add(obj)
            coords = Grid.all_coords(coord, obj.size)
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
        self.all_objs.remove(obj)
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
            obj_coord = self.player.subj_held_coord(new_coord)
            self.move_obj(player.held_obj, obj_coord)
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
        overlaps = coords1.union(coords2)
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
        self.register = coord_register
        self.coord = coord

    @property
    def all_objs(self):
        """
        Returns a set of all objects at this location
        """
        d = self.register.hashmap[self.coord]
        objs = set()
        for k in d.keys():
            objs = {*objs, *d[k]}
        return objs

    def __contains__(self, obj):
        d = self.register.hashmap[self.coord]
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
        if obj_type in self.register.hashmap[self.coord]:
            return self.register.hashmap[self.coord][obj_type]
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
        self.register.add(obj, self.coord)

    def remove(self, obj):
        """
        This function is used to quickly remove GameObjects from the
        CoordRegister at the coordinate that corresponds to this
        CoordSet

        Args:
            obj: GameObject
        """
        self.register.remove(obj, self.coord)
