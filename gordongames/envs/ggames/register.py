import Grid from grid

PLAYER = "player"
TARG = "targ"
PILE = "pile"
ITEM = "item"
DIVIDER = "divider"
BUTTON = "button"

OBJECT_TYPES = {
    PLAYER: PLAYER,
    TARG: TARG,
    PILE: PILE,
    ITEM: ITEM,
    DIVIDER: DIVIDER,
    BUTTON: BUTTON
}

STAY = 0
UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4

DIRECTIONS = {
    STAY: STAY,
    UP: UP,
    RIGHT: RIGHT,
    DOWN: DOWN,
    LEFT: LEFT
}

"""
colors: dict
    a dictionary to indicate what objects have what color
    items: (key: str, val: float)
      targ: the color of the target items
      pile: the color of the pile of items
      item: the color of individual items separated from the pile
      player: the color of the player
      button: the color of the ending button
"""
COLORS = {
    TARG: .4,
    PILE: .20,
    ITEM: .09,
    PLAYER: .69,
    DIVIDER: -.3,
    BUTTON: .17
}


class Register:
    """
    The register tracks the coordinates of all objects within the game.
    The possible objects are:
      targs - the target items for the game
      items - the moveable items for the game
      piles - the location for players to make and delete items
      players - the agents within the game
      dividers - a dividing line across the middle of the map to
        distinguish playable area from target area
      buttons - a button to press once the player thinks the task is
        finished
    
    The register has two data structures to track the items in the game.
    It has a set called obj_register that holds all of the GameObjects
    that are not dividers. It also has a dict called coord_register
    that maps coordinates to sets of items. Only coordintates with
    items are included in the coord_register.
    
    TODO:
      - way to determine if objects are on top of eachother
      - way to paint all objects to grid
      - way to wipe grid
    """
    def __init__(self,
                 grid: Grid,
                 n_targs: int):
        """
        Creates a player, a pile, and the specified number of targs.
        
        Args:
          grid: Grid
            the grid for the game
          n_targs: int
            the number of targets on the screen
        """
        self.grid = grid
        self.player = GameObject(obj_type=PLAYER, color=COLORS[PLAYER])
        self.pile = GameObject(obj_type=PILE, color=COLORS[PILE])
        self.button = GameObject(obj_type=BUTTON, color=COLORS[BUTTON])
        self.targs = self.make_targs(n_targs)
        self.items = set()
        self.obj_register = set(
            self.player,
            self.pile,
            self.button,
            *self.targs
        )
        self.coord_register = {
            (0,0): set(*self.obj_register)
        }
        for row in range(self.grid.shape[0]):
            for col in range(self.grid.shape[1]):
                coord = (row,col)
                if coord != (0,0):
                    self.coord_register[coord] = set()
    
    def make_targs(self, n_targs: int):
        """
        Creates the intial target objects
        
        Args:
          n_targs: int
            the number of targets to create
        """
        targs = set()
        for i in range(n_targs):
            targ = GameObject(
              obj_type=TARG,
              color=COLORS[TARG],
              coord=(0,0)
            )
            targs.add(targ)
        return targs
    
    def step(self, move: int, grab: int):
        """
        Step takes two actions and moves the player and any items
        appropriately.

        Args:
          move: int [0, 1, 2, 3, 4]
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
        did_move = self.move_object(self.player, move)
        if grab > 0:
            # Check for GameObject on player coordinate
            if self.player.coord in self.coord_register:
                # object exists

    def move_object(self, gameObject: GameObject, move:int):
        """
        Takes an object and updates its coordinate to reflect the move.
        Updates are reflected in coord_register

        Args:
            gameObject: GameObject
                the gameObject that is being moved
            move: int
                the movement direction. See DIRECTIONS constant
        """
        grid = self.grid
        move = move % len(DIRECTIONS)
        if move == UP:
            coord = (gameObject.coord[0]-1, gameObject.coord[1])
        elif move == RIGHT:
            coord = (gameObject.coord[0], gameObject.coord[1]+1)
        elif move == DOWN:
            coord = (gameObject.coord[0]+1, gameObject.coord[1])
        elif move == LEFT:
            coord = (gameObject.coord[0], gameObject.coord[1]-1)
        else:
            return
        in_bounds1 = grid.is_divided and grid.is_inhalfbounds(coord)
        in_bounds2 = not grid.is_divided and grid.is_inbounds(coord)
        if in_bounds1 or in_bounds2:
            gameObject.prev_coord = gameObject.coord
            gameObject.coord = (row, col)
            prev = gameObject.prev_coord
            if gameObject in self.coord_register[prev]:
                self.coord_register[prev].remove(gameObject)
            self.coord_register[coord].add(gameObject)
            return True
        return False

    def draw_register(self):
        """
        This function updates the grid with the current state of the
        register. It takes each GameObject and checks it for a
        coordinate change. If there is a change, the object is erased
        from its previous location and drawn to its new location.
        The GameObject is updated to reflect this update.
        """
        for obj in self.obj_register:
            if obj.prev_coord != obj.coord:
                self.grid.draw(
                    obj.prev_coord,
                    -obj.color,
                    add_color=True
                )
                self.grid_draw(
                    obj.coord,
                    obj.color,
                    add_color=True
                )
                obj.prev_coord = obj.coord

class GameObject:
    """
    The GameObject class is the main class for tracking what types of
    objects are on the grid. It contains the current coordinate and
    type of object.
    """
    def __init__(self,
                 obj_type: str,
                 color: float,
                 coord: list like=(0,0)):
        """
        obj_type: str
          the type of object. see OBJECT_TYPES for a list of available
          types.
        color: float
          the color of the object
        coord: list like (row, col) in grid units
          the initial coordinate of the object
        """
        self._obj_type = obj_type
        self._color = color
        self.coord = coord
        self.prev_coord = coord # used to track changes for drawing to grid

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

"""
Register

Need action system that can record direction as one hot and a grab
button.

Also need way of preventing agent from placing objects on top of each
other.

Action System:
  - Takes a direction and a grab signal
  - moves agent in direction (null direction okay)
  - if grab
    - checks register for carryable object (agent must be on top)
    - moves new item with agent if pile
    - moves current item with agent if item
  - Does all of this by controlling the register
"""
