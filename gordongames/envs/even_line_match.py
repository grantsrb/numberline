import os, subprocess, time, signal
import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gordongames.envs.ggames import Discrete, EvenLineMatchController
from gordongames.envs.ggames.constants import STAY
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib
except ImportError as e:
    raise error.DependencyNotInstalled("{}. (HINT: see matplotlib documentation for installation https://matplotlib.org/faq/installing_faq.html#installation".format(e))

class EvenLineMatch(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 targ_range=(1,10),
                 grid_size=(31,31),
                 pixel_density=5,
                 harsh=True):
        self.grid_size = grid_size
        self.pixel_density = pixel_density
        self.harsh = harsh
        self.viewer = None
        self.action_space = Discrete(6)
        self.is_grabbing = False
        self.controller = EvenLineMatchController(
            harsh=harsh,
            targ_range=targ_range,
        )
        self.controller.reset()

    def _toggle_grab(self):
        grab = not self.is_grabbing
        coord = self.controller.register.player.coord
        if self.is_grabbing:
            self.is_grabbing = False
        elif not self.controller.register.is_empty(coord):
            self.is_grabbing = True
        else:
            self.is_grabbing = False
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
        print("action: ", action)
        if action < 5:
            direction = action
            grab = self.is_grabbing
        else:
            direction = STAY
            grab = self._toggle_grab()
        self.last_obs,rew,done,info = self.controller.step(direction,
                                                           int(grab))
        return self.last_obs, rew, done, info

    def reset(self):
        self.controller.reset()
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
