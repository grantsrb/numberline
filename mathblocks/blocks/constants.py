PLAYER = "player"
PILE = "pile"
BLOCK = "block"
DIVIDER = "divider"
BUTTON = "button"
OPERATOR = "operator"
DEFAULT = "default"

OBJECT_TYPES = {
    PLAYER,
    PILE,
    BLOCK,
    DIVIDER,
    BUTTON,
    OPERATOR
}

ADD = "+"
SUBTRACT = "-"
MULTIPLY = "*"

OPERATORS = {
    ADD,
    SUBTRACT,
    MULTIPLY,
}

BLOCK_VALS = [1, 5, 10, 50, 100]
sizes = [(1,1), (5,1), (5,2), (10,5), (25,4)]
BLOCK_SIZES = {bv: size for bv, size in zip(BLOCK_VALS, sizes)}

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

BLOCK_COLORS = [
    0.07,
    0.15,
    0.23,
    0.39,
    0.43
]

COLORS = {
    PILE: 0.01,
    BLOCK: 0,
    PLAYER: -0.127,
    DIVIDER: -.3,
    BUTTON: -.2,
    DEFAULT: 0,
    OPERATOR: -0.08
}
for bv in BLOCK_VALS:
    COLORS[PILE+str(bv)] = COLORS[PILE] + bv
    COLORS[BLOCK+str(bv)] = COLORS[BLOCK] + bv

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
