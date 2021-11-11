import Grid from grid

PLAYER = "player"
TARG = "targ"
PILE = "pile"
ITEM = "item"
DIVIDER = "divider"

OBJECT_TYPES = {
  PLAYER: PLAYER,
  TARG: TARG,
  PILE: PILE,
  ITEM: ITEM,
  DIVIDER: DIVIDER
}

"""
colors: dict
  a dictionary to indicate what objects have what color
  items: (key: str, val: float)
    targ: the color of the target items
    pile: the color of the pile of items
    item: the color of individual items separated from the pile
    player: the color of the player
"""
COLORS = {
  TARG: .4,
  PILE: .20,
  ITEM: .09,
  PLAYER: .69,
  DIVIDER: -.3,
}


class Register:
  """
  The register tracks the coordinates of all objects within the game.
  5 types of objects exist. They are:
    targs - the target items for the game
    items - the moveable items for the game
    piles - the location for players to make and delete items
    players - the agents within the game
    dividers - a dividing line across the middle of the map to
      distinguish playable area from target area

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
    self.targs = self.make_targs(n_targs)
    self.items = set()
    self.obj_register = set(self.player, self.pile, *self.targs)
    self.coord_register = {
      (0,0): set(*self.obj_register)
    }

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
        0: move left (lower column unit)
        1: move up (lower row unit)
        2: move right (higher column unit)
        3: move down (higher row unit)
        4: no movement
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
    pass

  def draw_to_grid(self):
    """
    This function updates the grid with the current state of the
    registers.
    """
    pass

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
    the type of object. see OBJECT_TYPES for a list of available types.
  color: float
    the color of the object
  coord: list like (row, col) in grid units
    the initial coordinate of the object
  """
  self._obj_type = obj_type
  self._color = color
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
