from mathblocks.blocks.grid import Grid
from mathblocks.blocks.registry import Register
from mathblocks.blocks.constants import *
from mathblocks.blocks.utils import get_rows_and_cols, get_aligned_items, get_max_row, get_multiples_pairs
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
                 targ_range: tuple=(1,10),
                 grid_size: tuple=(31,31),
                 pixel_density: int=1,
                 max_num: int=500,
                 operators: set or list=OPERATORS,
                 *args, **kwargs):
        """
        targ_range: tuple (Low, High) (inclusive)
            the low and high number of target values for the game. Each
            displayed equation has a solution within this range.
        grid_size: tuple (Row, Col)
            the dimensions of the grid in grid units
        pixel_density: int
            the side length of a single grid unit in pixels
        max_num: int (inclusive)
            the maximum number that can be included in the display
            equation
        operators: set of str
            a sequence of potential operators to learn.
        """
        if type(targ_range) == int:
            targ_range = (targ_range, targ_range)
        assert targ_range[0] <= targ_range[1]
        assert grid_size[0] >= 2*BLOCK_SIZES[BLOCK_VALS[-1]][0]+10
        # Calculations ensure that both sides of the equation have
        # enough space for the maximum number plus 4 for the operator.
        # The max target is divided by two because the width
        # calculations multiply the block width by two for both sides
        # of the equation. This does not factor in spacing between
        # blocks
        if max(max_num, targ_range[1]//2) <= 10:
            assert grid_size[1] >= 14 # (1 + 4)*2 + 4
        elif max(max_num, targ_range[1]//2) <= 50:
            assert grid_size[1] >= 22 # (4 + 1 + 4)*2 + 4
        elif max(max_num, targ_range[1]//2) <= 100:
            assert grid_size[1] >= 32 # (5 + 4 + 1 + 4)*2 + 4
        elif max(max_num, targ_range[1]//2) <= 500:
            assert grid_size[1] >= 68 # (4*5 + 5 + 4 + 1 + 4)*2 + 4
        self._targ_range = targ_range
        self._grid_size = grid_size
        self._pixel_density = pixel_density
        self._operators = list(operators)
        self._max_num = max_num
        self.grid = Grid(
            grid_size=grid_size,
            pixel_density=pixel_density,
            divide=True
        )
        self.register = Register(grid=self.grid)

    @property
    def targ_range(self):
        return self._targ_range

    @property
    def grid_size(self):
        return self._grid_size

    @property
    def max_num(self):
        return self._max_num

    @property
    def operators(self):
        return self._operators

    @property
    def density(self):
        return self._pixel_density

    @property
    def max_punishment(self):
        return -self.targ_range[1]

    def calculate_reward(self):
        if self.register.block_sum == self.register.targ_val:
            return 1
        return -1

    def step(self, actn: int):
        """
        This function takes a step in the environment. The action can
        be a directional movement, a grab action, or a decomposition.

        Args:
          actn: int [0, 1, 2, 3, 4, 5, 6]
            Check DIRECTIONS to ensure these values haven't changed
                0: no movement
                1: move up (lower row unit)
                2: move right (higher column unit)
                3: move down (higher row unit)
                4: move left (lower column unit)
                5: grab (toggles the grab state)
                6: decompose (decomposes a block into smaller blocks)
        """
        if actn <= 4:
            self.register.move_player(actn)
        elif actn == 5:
            # handle drop is implicitly called if player is currently
            # holding an object
            self.register.handle_grab() 
        elif actn == 6:
            self.register.handle_decomp()
        info = {
            "n_blocks": self.register.n_blocks,
            "targ_val": self.register.targ_val,
            **self.register.block_counts,
        }
        done = False
        rew = 0
        if self.register.player.held_obj == self.register.button:
            rew = self.calculate_reward()
            done = True
        self.register.draw_register()
        return self.grid.grid, rew, done, info

    def reset(self, targ_val=None):
        """
        This member must be overridden
        """
        self.register.player.drop()
        self.register.clear_blocks()
        self.register.clear_eqn()
        self.register.set_nonblocks()
        if targ_val is None:
            targ_val = np.random.randint(
                self.targ_range[0],
                self.targ_range[1]+1
            )
        idx = np.random.randint(0, len(self.operators))
        operation = self.operators[idx]
        if operation == ADD:
            left = np.random.randint(0, targ_val+1)
            right = targ_val - left
        elif operation == SUBTRACT:
            left = np.random.randint(targ_val, self.max_num)
            right = left - targ_val
        elif operation == MULTIPLY:
            multiples = get_multiples_pairs(targ_val)
            m = multiples[np.random.randint(0, len(multiples))]
            idx = np.random.randint(0, 2)
            left = m[idx]
            right = m[1-idx]
        self.register.make_eqn(
            left_val=left,
            operation=operation,
            right_val=right
        )
        self.register.draw_register()
        return self.grid.grid

