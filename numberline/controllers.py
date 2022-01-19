from numberline.grid import Grid
from numberline.registry import Register
from numberline.constants import *
import numpy as np

"""
This file contains each of the game controller classes for each of the
Gordon games. 
"""

class Controller:
    """
    The base controller class for handling initializations. It is
    abstract and as such should not be implemented directly
    """
    def __init__(self,
                 pixel_density: int=5,
                 init_range: tuple=(0,0),
                 targ_range: tuple=(1,100),
                 op_range: tuple=(1,100),
                 operators: list or set={ADD, SUBTRACT},
                 is_discrete: bool=True,
                 zoom_range: tuple or None=None,
                 scroll_range: tuple or None=None,
                 ep_reset: bool=True,
                 *args, **kwargs):
        """
        pixel_density: int
            Number of numpy pixels making up the length and width of a
            single grid unit.
        init_range: tuple of ints
            A range of possible initial numberline values for each
            game (inclusive). Only used once if `ep_reset` is true.
        targ_range: tuple of ints
            A range of possible target solution counts for each game
            (inclusive).
        op_range: tuple of ints
            A range of possible operator number values for each game
            (inclusive).
        operators: list or set of str
            the operators you would like to include in the game. The
            available arguments are contained in
            `numberline.constants.OPERATORS`
        is_discrete: bool
            indicates if the operator and target number ranges should
            be discrete or continuous. true means numbers are discrete.
        zoom_range: tuple of inclusive floats | None
            indicates if the zoom should be restricted to finite
            amounts. 0 is a zoom level in which each unit represents
            a value of 1. A zoom of 1 is a level in which each unit
            represents 10. A zoom of -1 has each unit represent 0.1.
        scroll_range: tuple of inclusive ints | None
            if None, no limits are set on the ability to scroll left
            and right. Otherwise the argued integers represent the
            min and maximum scrollable values on the numberline. 
        ep_reset: bool
            if true, the value of the numberline resets after each
            episode. If false the value of the numberline persists
            through episodes.
        """
        if type(targ_range) == int:
            targ_range = (targ_range, targ_range)
        assert targ_range[0] <= targ_range[1]
        assert init_range[0] <= init_range[1]
        assert op_range[0] <= op_range[1]
        assert zoom_range is None or zoom_range[0] <= zoom_range[1]
        assert scroll_range is None or scroll_range[0]<=scroll_range[1]
        self._targ_range = targ_range
        self._pixel_density = pixel_density
        self._init_range = init_range
        self._op_range = op_range
        self._operators = list(operators)
        self._is_discrete = is_discrete
        self._zoom_range = zoom_range
        self._scroll_range = scroll_range
        self._ep_reset = ep_reset
        self.grid = Grid(pixel_density=pixel_density)
        self.register = Register(grid=self.grid)

    @property
    def targ_range(self):
        """
        A range of possible target solution counts for each game
        (inclusive).
        """
        return self._targ_range

    @targ_range.setter
    def targ_range(self, new_range):
        """
        new_range: tuple of ints
            A range of possible target solution counts for each game
            (inclusive).
        """
        self._targ_range = new_range

    @property
    def operators(self):
        return self._operators

    @operators.setter
    def operators(self, new_vals):
        """
        new_vals: list or set of str
            the operators you would like to include in the game. The
            available arguments are contained in
            `numberline.constants.OPERATORS`
        """
        self._operators = new_vals

    @property
    def density(self):
        return self._pixel_density

    @density.setter
    def density(self, new_density):
        """
        new_density: int
            Number of numpy pixels making up the length and width of a
            single grid unit.
        """
        self._pixel_density = new_density

    @property
    def init_range(self):
        return self._init_range

    @init_range.setter
    def init_range(self, new_range):
        """
        new_range: tuple of ints
            A range of possible initial numberline values for each
            game (inclusive). Only used once if `ep_reset` is true.
        """
        self._init_range = new_range

    @property
    def op_range(self):
        return self._op_range

    @op_range.setter
    def op_range(self, new_range):
        """
        new_range: tuple of ints
            A range of possible operand values for each game
            (inclusive).
        """
        self._op_range = new_range
        raise NotImplemented

    @property
    def is_discrete(self):
        return self._is_discrete

    @is_discrete.setter
    def is_discrete(self, new_val):
        """
        new_val: bool
            indicates if the operator and target number ranges should
            be discrete or continuous. true means numbers are discrete.
        """
        self._is_discrete = new_val

    @property
    def zoom_range(self):
        return self._zoom_range

    @zoom_range.setter
    def zoom_range(self, new_range):
        """
        new_range: tuple of inclusive floats | None
            indicates if the zoom should be restricted to finite
            amounts. 0 is a zoom level in which each unit represents
            a value of 1. A zoom of 1 is a level in which each unit
            represents 10. A zoom of -1 has each unit represent 0.1.
        """
        self._zoom_range = new_range

    @property
    def scroll_range(self):
        return self._scroll_range

    @scroll_range.setter
    def scroll_range(self, new_range):
        """
        new_range: tuple of inclusive ints | None
            if None, no limits are set on the ability to scroll left
            and right. Otherwise the argued integers represent the
            min and maximum scrollable values on the numberline. 
        """
        self._scroll_range = new_range

    @property
    def ep_reset(self):
        return self._ep_reset

    @ep_reset.setter
    def ep_reset(self, new_val):
        """
        new_val: bool
            if true, the value of the numberline resets after each
            episode. If false the value of the numberline persists
            through episodes.
        """
        self._ep_reset = new_val

    def calculate_reward(self):
        if self.register.fill == self.targ_val:
            return 1
        return -1

    def step(self, actn: int):
        """
        This function takes a step in the environment. The action can
        be a directional movement, a grab action, or a decomposition.

        Args:
          actn: int [0, 1, 2, 3, 4, 5, 6]
            Check IDX2ACTION dict to ensure these values haven't changed
                0: translate right
                1: translate left
                2: zoom in
                3: zoom out
                4: add value to numberline
                5: subtract value from numberline
                6: end episode
        """
        actn2fxn = {
            0: lambda: self.register.translate(1),
            1: lambda: self.register.translate(-1),
            2: self.register.zoom_in,
            3: self.register.zoom_out,
            4: lambda: self.register.add_fill(FILL_INCREMENT),
            5: lambda: self.register.add_fill(-FILL_INCREMENT),
            6: lambda: None,
        }

        # Perform the action within the register
        actn2fxn[actn]()

        info = {
            "fill": self.register.fill,
            "zoom": self.register.zoom,
            "operand": self.register.operand,
            "operator": self.register.operator,
            "trans": self.register.trans,
            "targ_val": self.targ_val,
        }
        done = False
        rew = 0
        if actn == ACTION2IDX[END_GAME]:
            done = True
            rew = self.calculate_reward()
        self.register.draw_register()
        return self.grid.grid, rew, done, info

    def reset(self, targ_val=None, operator=None, init_val=None):
        """
        This member must be overridden
        """
        self.register.reset(reset_fill=self.ep_reset)
        if init_val is None:
            init_val = np.random.randint(
                self.init_range[0],
                self.init_range[1]+1
            )
        self.register.fill = init_val
        if operator is None:
            i = np.random.randint(0, len(self.operators))
            operator = self.operators[i]
        if targ_val is None:
            targ_val = np.random.randint(
                self.targ_range[0],
                self.targ_range[1]+1
            )
        if operator == SUBTRACT:
            operand = self.register.fill - targ_val
        elif operator == ADD or self.register.fill == 0:
            operator = ADD
            operand = targ_val - self.register.fill
        elif operator == MULTIPLY:
            operand = targ_val/self.register.fill
        elif operator == DIVIDE:
            operand = targ_val*self.register.fill
        self.targ_val = targ_val
        self.operator = operator
        self.operand = operand
        self.register.operator = self.operator
        self.register.operand = self.operand
        self.register.draw_register()
        return self.grid.grid

