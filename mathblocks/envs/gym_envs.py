import os, subprocess, time, signal
import gym
from gym import error, spaces, utils
from gym.utils import seeding
from mathblocks.blocks import Discrete
from mathblocks.blocks.controllers import *
from mathblocks.blocks.constants import STAY, ITEM, TARG, PLAYER, PILE, BUTTON, OBJECT_TYPES
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib
except ImportError as e:
    raise error.DependencyNotInstalled("{}. (HINT: see matplotlib documentation for installation https://matplotlib.org/faq/installing_faq.html#installation".format(e))

class MathGame(gym.Env):
    """
    The base class for all mathblocks variants.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 targ_range=(1,10),
                 grid_size=(31,31),
                 pixel_density=5,
                 harsh=True,
                 *args, **kwargs):
        """
        Args:
            targ_range: tuple of ints (low, high) (both inclusive)
                the range of potential target counts for the game
            grid_size: tuple of ints (n_row, n_col)
                the dimensions of the grid in grid units
            pixel_density: int
                the number of pixels per unit in the grid
            harsh: bool
                changes the reward system to be more continuous if false
        """
        # determines the unit dimensions of the grid
        self.grid_size = grid_size
        # determines the number of pixels per grid unit
        self.pixel_density = pixel_density
        # tracks number of steps in episode
        self.step_count = 0
        # used in calculations of self.max_steps
        self.max_step_base = self.grid_size[0]//2*self.grid_size[1]*2
        # gets set in reset(), limits number of steps per episode
        self.max_steps = 0
        self.targ_range = targ_range
        if type(targ_range) == int:
            self.targ_range = (targ_range,targ_range)
        self.harsh = harsh
        self.viewer = None
        self.action_space = Discrete(6)
        self.is_grabbing = False
        self.set_controller()

    def set_controller(self):
        """
        Must override this function and set a member `self.controller`
        """
        self.controller = None # Must set a controller
        raise NotImplemented

    def _toggle_grab(self):
        grab = not self.is_grabbing
        coord = self.controller.register.player.coord
        if self.is_grabbing:
            self.is_grabbing = False
        # we know is_grabbing is false here
        elif not self.controller.register.is_empty(coord):
            self.is_grabbing = True
        return grab

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
        if action < 5:
            direction = action
            grab = self.is_grabbing
        else:
            direction = STAY
            grab = self._toggle_grab()
        self.last_obs,rew,done,info = self.controller.step(
            direction,
            int(grab)
        )
        player = self.controller.register.player
        info["grab"] = self.get_other_obj_idx(player, grab)
        if self.step_count > self.max_steps: done = True
        elif self.step_count == self.max_steps and rew == 0:
            rew = self.controller.max_punishment
            done = True
        return self.last_obs, rew, done, info

    def get_other_obj_idx(self, obj, grab):
        """
        Finds and returns an int representing the first game object
        that is not the argued object and is located at the locations
        of the argued object. 

        Args:
            obj: GameObject
            grab: bool
                the player's current grab state
        Returns:
            other_obj: GameObject or None
                one of the other objects located at this location.
                The priority goes by type, see `priority`
        """
        # Langpractice depends on this order
        priority = [
            PILE,
            BUTTON,
            ITEM,
            PLAYER,
            TARG,
        ]
        if not grab: return 0
        reg = self.controller.register.coord_register
        objs = {*reg[obj.coord]}
        if len(objs) == 1: return 0
        objs.remove(obj)
        memo = {o: set() for o in priority}
        # Sort objects
        for o in objs:
            memo[o.type].add(o)
        # return single object by priority
        for i,o in enumerate(priority):
            if len(memo[o]) > 0: return i+1
        return 0

    def reset(self, n_targs=None):
        self.controller.reset(n_targs=n_targs)
        self.max_steps = (self.controller.n_targs+1)*self.max_step_base
        self.is_grabbing = False
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

