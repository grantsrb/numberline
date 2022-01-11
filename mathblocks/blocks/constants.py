PLAYER = "player"
PILE = "pile"
BLOCK = "block"
DIVIDER = "divider"
BUTTON = "button"
OPERATOR = "operator"
DEFAULT = "default"

ADD = "+"
SUBTRACT = "-"
MULTIPLY = "*"

OPERATORS = {
    ADD,
    SUBTRACT,
    MULTIPLY,
}

BLOCK_VALS = sorted([1, 5, 10, 50, 100])
sizes = [(1,1), (5,1), (10,1), (10,5), (20,5)]
BLOCK_SIZES = {bv: size for bv, size in zip(BLOCK_VALS, sizes)}
BLOCK_TYPES = [BLOCK+str(val) for val in BLOCK_VALS]
PILE_TYPES = [PILE+str(val) for val in BLOCK_VALS]

DECOMP_COORDS = {
    BLOCK_VALS[1]: {(0,0), (1,0), (2,0), (3,0), (4,0)},
    BLOCK_VALS[2]: {(0,0), (5,0)},
    BLOCK_VALS[3]: {(0,0), (1,0), (2,0), (3,0), (4,0)},
    BLOCK_VALS[4]: {(0,0), (10,0)},
}

# The prioritization of which objects are grabbed if the agent is
# standing on overlapping objects
GRAB_ORDER = [
    BUTTON,
    *BLOCK_TYPES,
    *PILE_TYPES,
]

OBJECT_TYPES = {
    *GRAB_ORDER,
    PLAYER,
    DIVIDER,
    OPERATOR
}


STAY = 0
UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4
GRAB = 5
DECOMP = 6


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
    0.071,      
    0.0901,     
    0.11001,    
    0.130001,   
    0.1600001,  
]

COLORS = {
    PILE: 0.01,
    BLOCK: 0,
    PLAYER: 0.1712345,
    DIVIDER: -.3,
    BUTTON: -.2,
    DEFAULT: 0,
    OPERATOR: -0.08
}
for bv,bc in zip(BLOCK_VALS, BLOCK_COLORS):
    COLORS[PILE+str(bv)] = COLORS[PILE] + bc
    COLORS[BLOCK+str(bv)] = COLORS[BLOCK] + bc

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
