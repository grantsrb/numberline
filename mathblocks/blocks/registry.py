from mathblocks.blocks.grid import Grid
from mathblocks.blocks.constants import *
from mathblocks.blocks.utils import coord_diff, coord_add
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
        self.player_coord = coord
        self.player_color = color
        self.player_size = size
        self.grabbed_obj = None
        super().__init__(
            obj_type=PLAYER,
            color=color,
            coord=coord,
            size=size
        )

    def grab(self, obj):
        """
        Assists in grabbing a GameObject.

        Args:
            obj: GameObject
        """
        self.grabbed_obj = obj

    def drop(self):
        """
        Assists in dropping a GameObject.
        """
        self.grabbed_obj = None

    @property
    def is_grabbing(self):
        return self.grabbed_obj is not None

    @property
    def coord(self):
        return self.player_coord

    @coord.setter
    def coord(self, new_coord):
        """
        If the player is grabbing an object, the position of the object
        it is grabbing is also updated relative to the player's new
        position. The grabbed object's relative position to the player
        is maintained.
        """
        if self.is_grabbing:
            diff = coord_diff(new_coord, self.player_coord)
            self.player_coord = new_coord
            obj_coord = coord_add(self.grabbed_obj.coord, diff)
            self.grabbed_obj.coord = obj_coord
        else:
            self.player_coord = new_coord

class Pile(GameObject):
    """
    Piles are a special type of gameobject that allow creation of a
    new item of a particular size, color, and representative quantity.
    The Pile class holds the information for all new items created from
    itself.
    """
    def __init__(self, 
                 obj_type: str,
                 color: float,
                 block_val: int,
                 block_size: tuple,
                 block_color: float,
                 coord: tuple=(0,0),
                 size: tuple=(1,1)):
        """
        obj_type: str
          the type of object. see OBJECT_TYPES for a list of available
          types.
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
            obj_type=obj_type,
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
    It has a set called obj_register that holds all of the GameObjects
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
                obj_type=key,
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

        self.obj_register = {
            self.player,
            *self.piles.values(),
            self.button,
            self.operator
        }
        self.coord_register = CoordRegister(OBJECT_TYPES, grid.shape)
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
        s = 0
        for block in self.blocks:
            s += block.val
        return s

    def val2blocks(self, val):
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
        left_blocks = self.val2blocks(left_val)
        right_blocks = self.val2blocks(right_val)
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
        not impelmented

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

    #TODO: finish make_eqn func on 402
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

    def handle_drop(self, player):
        """
        This function is applied to the argued player's previous
        location. If any objects are overlapping they are handled as
        follows.
            item on pile: item is deleted
            item on item or button: item is placed in nearest empty
                location. see find_space() for details into the order
                of the search.

        Nothing happens if one or fewer objects resides at the player's
        prev_coord

        Args:
            player: GameObject
        """
        prev_objs = set(self.coord_register[player.prev_coord])
        assert len(prev_objs) < 4
        if len(prev_objs) > 1:
            # track the counts of each object type
            objs = {k: [] for k in OBJECT_TYPES}
            for obj in prev_objs:
                objs[obj.type].append(obj)
            # If there is an item on the coordinate and there is a
            # pile too, then we delete the item
            if len(objs[BLOCK]) > 0 and len(objs[PILE]) > 0:
                self.delete_obj(objs[BLOCK][0])
            # If there is an item and another item or a button,
            # then we find the nearest empty coordinate for one of the
            # items (they're interchangeable)
            elif len(objs[BLOCK]) > 1 or\
                    len(objs[BLOCK]) > 0 and len(objs[BUTTON]) > 0:
                free_coord = self.find_space(player.prev_coord)
                if free_coord is not None:
                    self.move_object(objs[BLOCK][0], free_coord)
                else:
                    return FULL
        return STEP

    def find_space(self, coord):
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
            return self.is_playable(loc) and self.is_empty(loc)
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

    def is_empty(self, coord):
        """
        A SPACE IS CONSIDERED EMPTY EVEN IF THE PLAYER OCCUPIES IT!!

        Checks if the argued coordinate is empty of GameObjects
        except for the player object. THE PLAYER OBJECT IS IGNORED!!!

        Args:
            coord: tuple in grid units (row, col)
        """
        coord = tuple(coord)
        if not self.grid.is_inbounds(coord): return False
        objs = self.coord_register[coord]
        if len(objs) == 0: return True
        elif len(objs) == 1 and self.player in objs: return True
        return False

    def is_playable(self, coord):
        """
        Determines if the coord is within playable bounds of the grid
        """
        return self.grid.is_playable(coord)

    def is_targ_space(self, coord):
        """
        Determines if the coord is within the space alotted for targets.
        If the grid is not divided, this means anywhere is fair game.
        If the grid is divided, then only the spaces below the middle
        line return true.
        """
        return self.grid.is_below_divider(coord)

    def is_overlapped(self, coord):
        """
        Checks if the argued coordinate has two or more GameObjects
        other than the player object. THE PLAYER OBJECT IS IGNORED!!!

        A SPACE IS NOT CONSIDERED TO OVERLAP IF THE PLAYER OCCUPIES IT
        WITH ANOTHER OBJECT!! THE PLAYER DOES NOT COUNT IN THIS
        FUNCTION!!

        Args:
            coord: tuple in grid units (row, col)
        Returns:
            is_overlapping: bool
                if true, multiple GameObjects other than the player
                object reside in this space
        """
        coord = tuple(coord)
        if not self.is_playable(coord): return False
        objs = self.coord_register[coord]
        if len(objs) > 2: return True
        elif self.player not in objs and len(objs) > 1: return True
        return False

    def delete_obj(self, game_object: GameObject):
        """
        Deletes the object from the registries and the grid

        Args:
            game_object: GameObject
                the gameobject to be deleted
        """
        self.grid.draw(
            game_object.prev_coord,
            -game_object.color,
            add_color=True
        )
        if game_object.coord in self.coord_register:
            self.coord_register[game_object.coord].remove(game_object)
        self.obj_register.remove(game_object)
        if game_object.type == TARG: self._targs.remove(game_object)
        elif game_object == self.player: del self.player
        elif game_object == self.button: del self.button
        elif game_object == self.pile: del self.pile
        else: del game_object

    def delete_items(self):
        """
        Deletes all items from the registers.
        """
        reg = {*self.obj_register}
        for obj in reg:
            if obj.type == BLOCK: self.delete_obj(obj)

    def handle_grab(self, player):
        """
        Assumes that a grab action was performed.

        Uses the previous and current coord of the argued player to
        handle any object interactions appropriately.

        The function operates as follows:
            create new item if previous location was a pile,
            raise button press event if previous location was a button,
            carry item to current coordinate if previous location
                was an item

        Args:
            player: GameObject
        """
        # copy set of objects residing in the previous location
        prev_objs = set(self.coord_register[tuple(player.prev_coord)])
        if len(prev_objs) > 0:
            for obj in prev_objs:
                if obj.type == BLOCK:
                    self.move_object(obj, coord=player.coord)
                    return STEP
            # Only possibility for 2 objects is if player is one of them
            if len(prev_objs) == 2 and player in prev_objs:
                prev_objs.remove(player)
            obj = prev_objs.pop()
            if obj.type == PILE:
                self.make_object(obj_type=BLOCK, coord=player.coord)
            elif obj.type == BUTTON:
                self.raise_button_event()
                return BUTTON_PRESS
        return STEP

    def make_object(self, obj_type: str, coord: tuple):
        """
        Creates a new instance of the argued object type at the argued
        coordinate. Automatically adds the object to the registers

        Args:
            obj_type: str
                the type of object. See OBJECT_TYPES for options
            coord: tuple in grid units (row, col)
                the intial coordinate of the object
        """
        coord = tuple(coord)
        obj = GameObject(
            obj_type=obj_type,
            color=COLORS[obj_type],
            coord=coord
        )
        self.obj_register.add(obj)
        self.coord_register[coord].add(obj)

    def apply_direction(self, coord: tuple, direction: int):
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

    def move_object(self, game_object: GameObject, coord: tuple=None):
        """
        Takes an object and updates its coordinate to reflect the
        argued coord. Updates are reflected in coord_register and in
        the argued game_object. Does not affect game_object's
        prev_coord value but does update its coord value.

        If object does not move, this function returns False. This
        includes if the action is STAY and successfully completed.

        Args:
            game_object: GameObject
                the game object that is being moved
            coord: tuple or None
                if this is argued and direction is None, the object
                is moved to this coord
        Returns:
            did_move: bool
                if true, the move was legal and object was moved.
                If false, the move was either illegal or did not change
                the game_object's coord value.
        """
        if coord == tuple(game_object.coord):
            return False
        if self.grid.is_inbounds(coord):
            prev = tuple(game_object.coord)
            game_object.coord = tuple(coord)
            if game_object in self.coord_register[prev]:
                self.coord_register[prev].remove(game_object)
            self.coord_register[coord].add(game_object)
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
        direction = direction % len(DIRECTIONS)
        coord = self.apply_direction(self.player.coord, direction)
        if self.grid.is_playable(coord):
            return self.move_object(self.player, coord)
        else:
            return False

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

        n_rows, n_cols = self.grid.shape
        for row in range(n_rows):
            for col in range(n_cols):
                coord = (row,col)
                if len(self.coord_register[coord]) > 0:
                    color = 0
                    for obj in self.coord_register[coord]:
                        color += obj.color
                        obj.prev_coord = tuple(obj.coord)
                    self.grid.draw(coord=coord, color=color)

    def draw_register_changes(self):
        """
        This function only updates the grid with changes made to the
        registered game objects. It searches for differences in 
        a GameObject's prev_coord and coord and updates the grid to
        reflect these changes.

        Each GameObject's prev_coord is updated to the value of coord.
        """
        for obj in self.obj_register:
            if obj.prev_coord != obj.coord:
                # Delete previous value
                self.grid.draw(
                    obj.prev_coord,
                    -obj.color,
                    add_color=True
                )
                # Add new value
                self.grid_draw(
                    obj.coord,
                    obj.color,
                    add_color=True
                )
                obj.prev_coord = obj.coord

    def rand_pile_button_player(self):
        """
        Places the pile, button, and player randomly along the top
        row of the grid.
        """
        cols = np.random.permutation(self.grid.shape[1])
        self.move_object(self.pile, (0, int(cols[0])))
        self.move_object(self.button, (0, int(cols[1])))
        self.move_object(self.player, (0, int(cols[2])))

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

    def register_button_event_handler(self, fxn):
        """
        Registers a function to be called on a button press event.

        Args:
            fxn: callable function
                the function to be called when a button press event
                occurs
        """
        self.button_event_registry.add(fxn)

    def register_full_grid_event_handler(self, fxn):
        """
        Registers a function to be called on a full grid event.

        Args:
            fxn: callable function
                the function to be called when a full grid event
                occurs
        """
        self.full_grid_event_registry.add(fxn)

    def raise_full_grid_event(self):
        """
        Called when the grid is completely full. Calls all functions
        registered in the full_grid_event_registry
        """
        for fxn in self.full_grid_event_registry:
            fxn()

    def raise_button_event(self):
        """
        Called when the button is pressed. Calls all functions in the
        button_event_registry
        """
        for fxn in self.button_event_registry:
            fxn()


class CoordRegister:
    """
    This class assists in tracking what GameObjects are located at each
    coordinate. The class holds a 2d array for each GameObject type.
    For each GameObject of within a type, an integer is added to all
    coordinates that are occupied by that GameObject.

    Use the function `move_object(obj, new_coord)` to update the internal
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
            coord_maps: dict
                this dict tracks where each object type lies on the
                actual grid by adding a +1 to every location on the
                corresponding ndarray

                keys: str
                    object types
                vals: ndarray
                    a map to track if an object of the corresponding
                    type is located at that coordinate
            hashmap: dict
                the hashmap is a dict that maps coordinates to dicts
                that map from object type strings to sets of the
                corresponding objects that are touching that location.
        """
        self.coord_maps = {ot: np.zeros(grid_shape) for ot in obj_types}
        self.hashmap = dict()
        for row in range(grid_shape[0]):
            for col in range(grid_shape[1]):
                coord = (row,col)
                self.hashmap[coord] = {ot: set() for ot in obj_types}

    def __getitem__(self, key):
        """
        Args:
            key: tuple of ints (Row, Col)
                the coordinate location in grid units
        Returns:
            objs: set of GameObjects
                all objects that are partially touching that location
        """
        return CoordSet(self, tuple(key))

    def add(self, obj, coord=None):
        """
        Adds a new object to the hashmap

        Args:
            obj: GameObject
            coord: tuple of ints (row, col) or None
                if None, obj.coord is used instead
        """
        if coord is None: coord = obj.coord
        coords = Grid.all_coords(coord, obj.size)
        for c in coords:
            if obj.type in self.hashmap[c]:
                self.hashmap[c][obj.type].add(obj)
            else:
                self.hashmap[c][obj.type] = {obj}

    def remove(self, obj, coord=None):
        """
        Removes an object from the hashmap

        Args:
            obj: GameObject
            coord: tuple of ints (row, col) or None
                if None, all possible coordinates are searched to
                ensure the object is completely removed
        """
        if coord is None:
            coords = self.hashmap.keys()
        else:
            coords = Grid.all_coords(coord, obj.size)
        for c in coords:
            if obj in self.hashmap[c][obj.type]:
                self.hashmap[c][obj.type].remove(obj)

    def move_object(self, obj, old_coord, new_coord):
        """
        Moves the GameObject from its current coordinate to the argued
        new coord. Assumes the GameObject's current coordinate is
        represented by its `coord` member variable.

        Args:
            obj: GameObject
            old_coord: tuple of ints (row, col)
                the old coordinate in grid units
            new_coord: tuple of ints (row, col)
                the new coordinate in grid units
        """
        # Collect coordinate sets
        old_coords = Grid.all_coords(old_coord, obj.size)
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

    def __contains__(self, obj):
        d = self.register.hashmap[coord]
        if obj.type in d:
            return obj in d[obj.type]
        return False

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
