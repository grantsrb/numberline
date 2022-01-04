import mathblocks as mb
import numpy as np

class Oracle:
    def __call__(self, env=None, state=None):
        """
        All oracles must implement this function to operate on the
        environment.

        Args:
            env: None or SequentialEnvironment
                the environment to be acted upon. if None, state must
                be not None
            state: None or torch FloatTensor
                the environment to be acted upon. if None, env must
                be not None.
        """
        raise NotImplemented

class NullOracle(Oracle):
    def __call__(self, *args, **kwargs):
        return 0

class RandOracle(Oracle):
    def __init__(self, actn_min=0, actn_max=5):
        self.brain = lambda: np.random.randint(actn_min, actn_max)

    def __call__(self, *args, **kwargs):
        return self.brain()

class CountingOracle(Oracle):
    def __init__(self, env_type, *args, **kwargs):
        self.env_type = env_type
        self.is_grabbing = False
        
        if self.env_type == "mathblocks-v0":
            self.brain = mb.blocks.ai.counting
        else:
            raise NotImplemented
        print("brain:", type(self.brain))

    def __call__(self, env, *args, **kwargs):
        """
        Args:
            env: SequentialEnvironment
                the environment
        """
        (direction, grab) = self.brain(env.controller)
        if grab == self.is_grabbing:
            return direction
        else:
            self.is_grabbing = grab
            return 5
