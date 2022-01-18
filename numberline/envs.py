import os, subprocess, time, signal
import gym
from gym import error, spaces, utils
from gym.utils import seeding
from numberline import Discrete
from numberline.controllers import *
from numberline.constants import *
from numberline.utils import decompose
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib
except ImportError as e:
    raise error.DependencyNotInstalled("{}. (HINT: see matplotlib documentation for installation https://matplotlib.org/faq/installing_faq.html#installation".format(e))


class NumberLine(gym.Env):
    """
    The base class for all mathblocks variants.
    """
    metadata = {'render.modes': ['human']}

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
        self._targ_range = targ_range
        self._pixel_density = pixel_density
        self._init_range = init_range
        self._op_range = op_range
        self._operators = list(operators)
        self._is_discrete = is_discrete
        self._zoom_range = zoom_range
        self._scroll_range = scroll_range
        self._ep_reset = ep_reset

        # ENVIRONMENT SPECIFIC MEMBERS
        # tracks number of steps in episode
        self.step_count = 0
        # limits number of steps per episode. Set in `self.reset()`
        self.max_steps = 0
        self.viewer = None
        self.action_space = Discrete(7)
        self.set_controller()
        self.grid = self.controller.grid
        self.register = self.controller.register

    def set_controller(self):
        """
        Must override this function and set a member `self.controller`
        """
        self.controller = Controller(
            pixel_density=self.density,
            init_range=self.init_range,
            targ_range=self.targ_range,
            op_range=self.op_range,
            operators=self.operators,
            is_discrete=self.is_discrete,
            zoom_range=self.zoom_range,
            scroll_range=self.scroll_range,
            ep_reset=self.ep_reset
        )

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
        self.controller.targ_range = new_range

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
        self.controller.operators = new_vals

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
        self.controller.density = new_density

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
        self.controller.init_range = new_range

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
        self.controller.op_range = new_range
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
        self.controller.is_discrete = new_val

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
        self.controller.zoom_range = new_range

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
        self.controller.scroll_range = new_range

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
        self.controller.ep_reset = new_val

    def step(self, action):
        """
        Args:
            action: int
                the action should be an int of either a direction or
                a grab command
                    0: null action
                    1: move up one unit
                    2: move right one unit
                    3: move down one unit
                    4: move left one unit
                    5: grab/drop object
        Returns:
            last_obs: ndarray
                the observation
            rew: float
                the reward
            done: bool
                if true, the episode has ended
            info: dict
                whatever information the game contains
        """
        self.step_count += 1
        self.last_obs,rew,done,info = self.controller.step(action)
        if self.step_count > self.max_steps: done = True
        elif self.step_count == self.max_steps and rew == 0:
            rew = -1
            done = True
        return self.last_obs, rew, done, info

    def reset(self, targ_val=None, operator=None):
        self.controller.reset(
            targ_val=targ_val,
            operator=operator
        )
        self.max_steps = ARBITRARY_MAX_STEPS
        self.step_count = 0
        self.last_obs = self.controller.grid.grid
        return self.last_obs

    def render(self, mode='human', close=False, frame_speed=.1):
        if self.viewer is None:
            self.fig = plt.figure()
            self.viewer = self.fig.add_subplot(111)
            plt.ion()
            self.fig.show()
        else:
            self.viewer.clear()
            self.viewer.imshow(self.last_obs)
            plt.pause(frame_speed)
        self.fig.canvas.draw()

    def seed(self, x):
        np.random.seed(x)

