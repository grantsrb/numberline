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
        self.targ_range = targ_range
        if type(targ_range) == int:
            self.targ_range = (targ_range,targ_range)
        self.grid_size = grid_size
        self.pixel_density = pixel_density
        self.max_num = max_num
        self.operators = operators

        # tracks number of steps in episode
        self.step_count = 0
        # used in calculations of self.max_steps
        self.max_step_base = self.grid_size[0]//2*self.grid_size[1]*2
        # gets set in reset(), limits number of steps per episode
        self.max_steps = 0
        self.viewer = None
        self.action_space = Discrete(7)
        self.set_controller()

    def set_controller(self):
        """
        Must override this function and set a member `self.controller`
        """
        self.controller = Controller(
            targ_range=self.targ_range,
            grid_size=self.grid_size,
            pixel_density=self.pixel_density,
            max_num=self.max_num,
            operators=self.operators
        )

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
        player = self.controller.register.player
        info["grab"] = self.get_held_obj_idx(player)
        if self.step_count > self.max_steps: done = True
        elif self.step_count == self.max_steps and rew == 0:
            rew = -1
            done = True
        return self.last_obs, rew, done, info

    def get_held_obj_idx(self, player):
        """
        Returns an integer representing what type of object the player
        is holding. If the player is on top of a pile and holding an
        object, then the pile is recorded instead of the object.

            Nothing: 0
            Pile: 1
            Block: 2
            Button: 3

        Args:
            player: Player
        Returns:
            other_obj_type: int
                an integer representing the object that the player
                is holding. If player is on top of a pile while holding
                a block, the pile is recorded as the object the player
                is holding.

                Returns 0 if player is not holding an object.
        """
        if not player.is_holding: return 0
        pcoords = {
          v.coord for v in self.controller.register.piles.values()
        }
        if player.coord in pcoords: return 1
        if player.held_obj == self.controller.register.button:
            return 3
        return 2

    def reset(self, targ_val=None):
        self.controller.reset(targ_val=targ_val)
        atoms = decompose(self.controller.register.targ_val, BLOCK_VALS)
        n_atoms = np.sum(list(atoms.values()))
        self.max_steps = (n_atoms+1)*self.max_step_base
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

