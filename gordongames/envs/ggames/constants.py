PLAYER = "player"
TARG = "targ"
PILE = "pile"
ITEM = "item"
DIVIDER = "divider"
BUTTON = "button"
DEFAULT = "default"

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

DIRECTION2STR = {
    STAY:  "STAY",
    UP:    "UP",
    RIGHT: "RIGHT",
    DOWN:  "DOWN",
    LEFT:  "LEFT"
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
    BUTTON: -.1,
    DEFAULT: 0,
}

"""
The events are used in the game to signal what type of event occurred
at each step.

    STEP: nothing of interest occurred
    BUTTON: the ending button was pressed by the player
    FULL: the grid is full of objects
"""
STEP = 0
BUTTON_PRESS = 1
FULL = 2

EVENTS = {
    STEP: STEP,
    BUTTON_PRESS: BUTTON_PRESS,
    FULL: FULL,
}
