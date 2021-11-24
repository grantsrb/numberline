from gordongames.envs.ggames.grid import Grid
from gordongames.envs.ggames.registry import Register
from gordongames.envs.ggames.constants import *
from gordongames.envs.ggames.utils import get_rows_and_cols
import numpy as np

"""
This file contains each of the game controller classes for each of the
Gordon games. 
"""

class Controller:
    """
    The base controller class for handling initializations
    """
    def __init__(self,
                 targ_range: tuple=(1,10),
                 grid_size: tuple=(31,31),
                 pixel_density: int=1,
                 *args, **kwargs):
        """
        targ_range: tuple (Low, High) (inclusive)
            the low and high number of targets for the game. each
            episode is intialized with a number of targets within
            this range.
        grid_size: tuple (Row, Col)
            the dimensions of the grid in grid units
        pixel_density: int
            the side length of a single grid unit in pixels
        """
        if type(targ_range) == int:
            targ_range = (targ_range, targ_range)
        assert targ_range[0] <= targ_range[1]
        assert targ_range[0] >= 0 and targ_range[1] < grid_size[1]
        self._targ_range = targ_range
        self._grid_size = grid_size
        self._pixel_density = pixel_density

    @property
    def targ_range(self):
        return self._targ_range

    @property
    def grid_size(self):
        return self._grid_size

    @property
    def density(self):
        return self._pixel_density

    def calculate_reward(self):
        raise NotImplemented

    def step(self, direction: int, grab: int):
        """
        Step takes a movement and a grabbing action. The function
        moves the player and any items in the following way.

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
        event = self.register.step(direction, grab)
        info = {
            "is_harsh": self.harsh,
            "n_targs": self.register.n_targs,
        }
        if event == BUTTON_PRESS:
            rew = self.calculate_reward(harsh=self.harsh)
            done = True
        elif event == FULL:
            done = True
            rew = -1
        elif event == STEP:
            done = False
            rew = 0
        return self.grid.grid, rew, done, info

class EvenLineMatchController(Controller):
    """
    This class creates an instance of an Even Line Match game.

    The agent must align a single item along the column of each of the
    target objects.
    """
    def __init__(self, harsh: bool=False, *args, **kwargs):
        """
        See base Controller class for details into arguments.
        
        Args:
            harsh: bool
                if true, returns a postive 1 reward only upon successful
                completion of an episode. if false, returns the
                number of correct target columns divided by the total
                number of columns minus the total number of
                incorrect columns divided by the total number of
                columns.

                harsh == False:
                    rew = n_correct/n_total - n_incorrect/n_total
                harsh == True:
                    rew = n_correct == n_targs
        """
        super().__init__(*args, **kwargs)
        self.grid = Grid(
            grid_size=self.grid_size,
            pixel_density=self.density,
            divide=True
        )
        self.register = Register(self.grid, n_targs=1)
        self.harsh = harsh

    def reset(self):
        """
        This function should be called everytime the environment starts
        a new episode.
        """
        low, high = self.targ_range
        n_targs = np.random.randint(low, high+1)
        # wipes items from grid and makes/deletes targs
        self.register.reset(n_targs)
        # randomizes object placement on grid
        self.register.even_line_match()
        return self.grid.grid

    def calculate_reward(self, harsh: bool=False):
        """
        Determines what reward to return. In this case, checks if
        the same number of items exists as targets and checks that
        all items are in a single row and that an item is in each
        column that contains a target. If all of these factors are
        met, if harsh is true, the function returns a reward of 1.
        If harsh is false, the function returns a partial reward
        based on the portion of columns that were successfully filled
        minus the portion of incorrect columns.

        Args:
            harsh: bool
                if true, returns a postive 1 reward only upon successful
                completion of an episode. if false, returns the
                number of correct target columns divided by the total
                number of columns minus the total number of
                incorrect columns divided by the total number of
                columns.

                harsh == False:
                    rew = n_correct/n_total - n_incorrect/n_total
                harsh == True:
                    rew = n_correct == n_targs
        Returns:
            rew: float
                the calculated reward
        """
        targs = self.register.targs
        items = self.register.items
        if harsh:
            if len(targs) != len(items): return 0

        item_rows, item_cols = get_rows_and_cols(items)
        _, targ_cols = get_rows_and_cols(targs)

        if len(item_rows) > 1: return 0
        if harsh:
            return int(targ_cols == item_cols)
        else:
            intersection = targ_cols.intersection(item_cols)
            rew = len(intersection)
            rew -= (len(item_cols)-len(intersection))
            rew -= max(0, len(items)-len(targs))
            return rew / self.grid.shape[1]

class ClusterLineMatchController(EvenLineMatchController):
    """
    This class creates an instance of a Cluster Line Match game.

    The agent must place a cluster of items matching the number of
    target objects. The items must not be all in a single row and
    must not all be aligned with the target columns.
    """
    def calculate_reward(self, harsh: bool=False):
        """
        Determines what reward to return. In this case, checks if
        the same number of items exists as targets and checks that
        all items are not in a single row and that the items do not
        align perfectly in the target columns.
        
        If all of these factors are met, if harsh is true, the
        function returns a reward of 1. If harsh is false, the
        function returns a partial reward based on the difference of
        the number of items to targs divided by the number of targs.
        A 0 is returned if all items are aligned with targs or if all
        items are in a single row.

        Args:
            harsh: bool
                if true, the function returns a reward of 1 when the
                same number of items exists as targs and the items are
                not aligned in a single row with the targ columns.
                If harsh is false, the function returns a partial
                reward based on the difference of the number of items
                to targs divided by the number of targs.
                A 0 is returned in both cases if all items are aligned
                with targs or if all items are in a single row.

                harsh == False:
                    rew = (n_targ - abs(n_item-n_targ))/n_targ
                harsh == True:
                    rew = n_items == n_targs
        Returns:
            rew: float
                the calculated reward
        """
        targs = self.register.targs
        items = self.register.items
        n_targs = len(targs)
        n_items = len(items)
        if harsh and n_targs != n_items: return 0
        item_rows, item_cols = get_rows_and_cols(items)
        _, targ_cols = get_rows_and_cols(targs)
        if len(item_rows) == 1 or targ_cols == item_cols: return 0
        # already know same number of items as targs if harsh
        if harsh: return 1
        else: return 1 - np.abs(n_item-n_targ)/n_targ

class UnevenLineMatchController(EvenLineMatchController):
    """
    This class creates an instance of an Uneven Line Match game.

    The agent must align a single item along the column of each of the
    target objects. The target objects are unevenly spaced.
    """
    def reset(self):
        """
        This function should be called everytime the environment starts
        a new episode.
        """
        low, high = self.targ_range
        n_targs = np.random.randint(low, high+1)
        # wipes items from grid and makes/deletes targs
        self.register.reset(n_targs)
        # randomizes object placement on grid
        self.register.uneven_line_match()
        return self.grid.grid

class OrthogonalLineMatchController(EvenLineMatchController):
    """
    This class creates an instance of an Orthogonal Line Match game.

    The agent must align the same number of items as targs. The items
    must be aligned vertically and evenly spaced by 0 if the targs are
    spaced by 0 or items must be spaced by 1 otherwise.
    """
    def calculate_reward(self, harsh: bool=False):
        """
        Determines what reward to return. In this case, checks if
        the same number of items exists as targets and checks that
        all items are evenly spaced along a single column. If the targs
        are spaced by 0, the items should be spaced by 0. Otherwise the
        items should be spaced by 1.

        Args:
            harsh: bool
                if true, the function returns a reward of 1 when the
                same number of items exists as targs and the items are
                aligned in a single column, properly spaced. 0
                otherwise.
                If harsh is false, the function returns a partial
                reward based on the difference of the number of items
                to targs divided by the number of targs. Extraneous
                spaces and items are subtracted from the reward when
                harsh is False

                harsh == False:
                    rew = (n_targ - abs(n_item-n_targ))/n_targ - n_extra
                harsh == True:
                    rew = n_items == n_targs
        Returns:
            rew: float
                the calculated reward
        """
        targs = self.register.targs
        items = self.register.items
        n_targs = len(targs)
        n_items = len(items)
        if harsh:
            if n_targs != n_items: return 0
        _, item_cols = get_rows_and_cols(items)
        item_rows = sorted([i.coord[0] for i in items])
        targ_cols = sorted([t.coord[1] for t in targs])
        targ_spacing = min((targ_cols[1]-targ_cols[0])-1, 1)

        count_error = 1-np.abs(n_item-n_targ)/n_targ
        spacing_error = self.calc_spacing_error(item_rows,targ_spacing)
        col_error = len(item_cols) - 1
        if harsh:
            if col_error > 0 or spacing_error > 0: return 0
            else: return 1
        return count_error - spacing_error - col_error

    def calc_spacing_error(self, arr: list, targ_spacing: int):
        """
        Calculates the total amount of misspacing. If the distance
        between two adjoined values is not equal to targ_spacing, the
        value is added to the total error.

        Args:
            arr: sorted list of ints in ascending order
            targ_spacing: int
                any distances between arr[i+1] and arr[i] are compared
                to this value. If different, 1 is added to the error.
        Returns:
            error: int
                the number of misspaced values in the array
        """
        error = 0
        for i in range(len(arr)-1):
            er = int((arr[i+1]-arr[i])!=targ_spacing)
            error += er
        return error
        

