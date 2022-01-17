ARBITRARY_MAX_STEPS = 30
# GENERAL
OPERATOR = "operator"
DEFAULT = "default"
FILL = "fill"
MARKER = "marker"
MARKER_BASE = "marker_base"
ZERO = "zero"

# Operations
ADD = "add"
SUBTRACT = "subtract"
MULTIPLY = "multiply"
DIVIDE = "divide"
OPERATORS = {
    ADD,
    SUBTRACT,
    MULTIPLY,
    DIVIDE
}
OPERATOR2SYMBOL = {
    ADD: "+",
    SUBTRACT: "-",
    MULTIPLY: "*",
    DIVIDE: "/"
}


# Actions
RIGHT = "right"
LEFT = "left"
ZOOM_IN = "zoom_in"
ZOOM_OUT = "zoom_out"
ADD_ONE = "add_one"
SUBTRACT_ONE = "take_one"
END_GAME = "end_game"
actns = [
    RIGHT,
    LEFT, 
    ZOOM_IN,
    ZOOM_OUT,
    ADD_ONE,
    SUBTRACT_ONE,
    END_GAME,
]
ACTION2IDX = {actn: i for i,actn in enumerate(actns)}
IDX2ACTION = {i: actn for i,actn in enumerate(actns)}


# COLORS
COLORS = {
    DEFAULT: 0,
    ZERO: -0.258923,
    MARKER: -0.16719,
    MARKER_BASE: 0.05111,
    FILL: 0.23317,

    # OPERATORS
    ADD: 0.2,
    SUBTRACT: -0.2,
    MULTIPLY: 0.4,
    DIVIDE: -0.4,
}

# The amount that the fill changes when adding and subtracting fill.
FILL_INCREMENT = 1 

# The amount that the raw value is divided by to find a pixel value for
# each value
ZOOM_DIVISOR = 10
OPERAND_DIVISOR = 100
TRANS_DIVISOR = 100
