from numberline.grid import Grid
from numberline.constants import *
import math
import numpy as np

class Register:
    """
    The register handles tracking the meta variables of the game.
    i.e. the register tracks where the state of the game is in space,
    the current zoom level, the operators, the operator numbers, etc
    """
    def __init__(self, grid: Grid):
        """
        Args:
          grid: Grid
            the grid for the game
        """
        self.grid = grid
        self.reset()
        self.draw_register()

    def reset(self, reset_fill=True):
        """
        Resets all member variables to their initial values.

        Args:
            reset_fill: bool
                if false, the fill is not reset so as to preserve state
                across multiple episodes.
        """
        if reset_fill:
            self._fill = 0
        self._zoom = 0
        self._operator = ADD
        self._operand = 0
        self._trans = 0


    @property
    def fill(self):
        """
        Returns the current value of the number line.

        Returns:
            fill: int
                the amount of space that should be colored along the
                numberline
        """
        return self._fill

    @fill.setter
    def fill(self, new_fill):
        self._fill = new_fill

    @property
    def zoom(self):
        """
        Returns the current zoom value of the game. Zoom values are
        the log base 10 of the value of a single grid unit. So, when,
        for example, the grid displays the numbers 0-100 in which each
        grid unit represents 1 numberline value, then the zoom is 0. If
        we zoomed out one level, 1 grid unit would represent 10 and
        thus the zoom level would be 1. And zooming in one level from
        the zoom level of 0, we would see 1 grid unit has a value of
        0.1. The zoom for this level would be -1.

        Returns:
            zoom: int
        """
        return self._zoom

    @property
    def operator(self):
        """
        Returns the current state of the operator.

        Returns:
            operator: str
                to convert the string to a color, use the COLORS dict
        """
        return self._operator

    @operator.setter
    def operator(self, new_operator):
        """
        Args:
            new_operator: str
                the new operator. see `constants.OPERATORS` for
                possible values
        """
        self._operator = new_operator

    @property
    def operand(self):
        """
        Returns the current state of the operand. This number
        is intended to be used in conjunction with the numberline and
        the operator to form an equation:

            numline operator operand = target_value

        Returns:
            operand: float
                the value of the operand
        """
        return self._operand

    @operand.setter
    def operand(self, new_operand):
        """
        Args:
            new_operand: float
                the new operand.
        """
        self._operand = new_operand

    @property
    def trans(self):
        """
        Returns the current state of translation from the 0 point,
        measured in grid units. The state of translation is tracked as
        an integer representing the number of grid units that the
        center of the screen (idx 50) is from the value of 0. Thus
        when the game zooms in, the trans value is immediately increased
        by a factor of 10. Similarly, when the game zooms out, the trans
        value is reduced by a factor of 10, rounded to the nearest
        integer.

        Returns:
            trans: float
                the number of units that the center of screen is away
                from the 0 marker on the numberline. trans has
                directionality
        """
        return self._trans

    @trans.setter
    def trans(self, new_trans):
        """
        Directly sets the translation position

        Args:
            new_trans: float
                the new translation value
        """
        self._trans = new_trans

    def add_fill(self, additive):
        """
        If you just want to add a particular amount to the fill without
        doing the math of how this would affect the final fill, use 
        this function.

        Args:
            additive: float
                the amount to change the current fill by
        """
        self._fill += additive*(10**self.zoom)

    def unit2val(self, unit):
        """
        Converts a unit distance from the 0 point to a value on the
        current zoom level of the numberline

        Args:
            unit: int
                the number of units away from the zero point on the
                numberline
        """
        return unit*10**self.zoom

    def get_markers(self):
        """
        This function returns the coordinates and color values of each
        location in the current view that should be marked as a 10s
        place or 5's place.

        Returns:
            cols: list of ints
                the column indices that should be marked
            colors: list of floats
                the color that should be marked in the corresponding
                column
        """
        cols = []
        colors = []
        for col in range(self.grid.shape[1]):
            color = 0
            # Distance from the 0 point on the number line
            dist = self.trans - self.grid.middle + col
            # full marker color if 10s place
            if dist != 0 and np.abs(dist) % 10 == 0:
                cols.append(col)
                log10 = int(np.log10(np.abs(self.unit2val(dist))))
                color = log10*COLORS[MARKER]+COLORS[MARKER_BASE]
                colors.append(color)
            # half marker color if 5s place
            elif dist != 0 and (np.abs(dist)+5) % 10 == 0:
                dist = np.abs(dist)+5
                cols.append(col)
                log10 = int(np.log10(np.abs(self.unit2val(dist))))
                color = log10*COLORS[MARKER]+COLORS[MARKER_BASE]
                colors.append(color/2)
        return cols, colors

    def draw_markers(self, add_color=True):
        """
        Places marker values every 10 units out from the zero point.
        Every 100 units is marked as 2*marker_color, every 1*10^x units is
        marked as x*marker_color

        Args:
            add_color: bool
                if true, the color is added to the existing color at
                each marker coordinate. If false, the color at the
                marker coordinate is set to the marker color
        """
        # list of coordinates and their log base 10 coordinate value
        cols, colors = self.get_markers()
        for col, color in zip(cols, colors):
            self.grid.draw(col, color=color, add_color=add_color)

    def translate(self, direction):
        """
        Takes a direction and updates the player's perspective to
        reflect an applied translation. 

        Args:
            direction: str
                the argued value translates the game's perspective
                that many grid units
        """
        self._trans += direction

    def zoom_in(self):
        """
        Zooms in one notch. Sets the value of a single grid unit to
        0.1 of its current value.
        """
        self._zoom -= 1
        self._trans = self.trans*10

    def zoom_out(self):
        """
        Zooms out one notch. Sets the value of a single grid unit to
        10 of its current value.
        """
        self._zoom += 1
        self._trans = int(self.trans/10)

    def zero_idx(self):
        """
        Finds and returns the column index on the grid that represents
        the zero point on the numberline. If the zero point is not
        currently visible, returns None.

        Returns:
            zero_idx: int
                the grid unit in which the zero point of the numberline
                is currently residing.
        """
        # Remember that trans always marks the number of grid units
        # between the zero point and the center of the visible grid.
        # So, if trans is greater than self.grid.middle, the zero point
        # will not be visible. If trans is less than -self.grid.middle
        # then the zero point will also not be visible.
        return self.grid.middle - self.trans

    def draw_register(self):
        """
        This function updates the grid with the current state of the
        register.

        The draw process wipes the grid to the default value, then for
        each coordinate all GameObjects at that coordinate sum their
        colors together which is then drawn to the grid at that coord.
        """
        # clears all information on the grid but maintains intial
        # ndarray reference self.grid._grid.
        self.grid.clear()
        self.grid.set_zoom_color(self.zoom/ZOOM_DIVISOR)
        self.grid.set_operator_color(COLORS[self.operator])
        self.grid.set_operand_color(self.operand/OPERAND_DIVISOR)
        self.grid.set_trans_color(self.trans/TRANS_DIVISOR)
        zero_idx = self.zero_idx()
        if self.grid.col_inbounds(zero_idx):
            self.grid.draw(
                zero_idx,
                color=COLORS[ZERO],
                add_color=False
            )
        self.draw_markers()
        if self.fill != 0:
            startx, endx = self.get_fill_range(zero_idx)
            if startx is not None and endx is not None:
                self.grid.draw_fill(startx, endx)

    def get_fill_range(self, zero_idx):
        """
        Converts the fill amount to a range of column indices on the
        grid depending on the zoom and the translation values.

        Args:
            zero_idx: int
                the grid index in which the zero point on the numberline
                exists
        Returns:
            startx: int
                the column (inclusive) on the grid that the filling
                should start at.
            endx: int
                the column (exclusive) on the grid that the filling
                should stop at.
        """
        # Column indices
        middle = self.grid.middle
        end = self.grid.shape[1]
        # Unit indexes from the index of the 0 point on the numberline
        # 0 grid index is col0ufz units away from numline zero
        col0ufz = self.trans-middle 
        # zoom is 1 when grid units are each 1 value
        # zoom is the log base 10 of the value that a single grid unit
        # represents whereas self.fill is the floating point value
        # that the numberline is supposed to represent
        fill_units = int(self.fill / (10**self.zoom))
        if fill_units == 0: return None, None
        fillx = fill_units - col0ufz
        # Need to add onto the zero index and the fill index to ensure
        # that the zero index is left unfilled
        if fillx > zero_idx: startx, endx = zero_idx+1, fillx+1
        elif fillx < zero_idx: startx, endx = fillx, zero_idx
        else: return None, None # no fill 
        if startx < end: startx = max(startx, 0)
        if endx > 0: endx = min(end, endx)
        if startx >= endx: return None, None
        return startx, endx

