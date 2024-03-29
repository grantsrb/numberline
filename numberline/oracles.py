from numberline.ai import zoom_solution
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
    def __init__(self, actn_min=0, actn_max=6):
        self.brain = lambda: np.random.randint(actn_min, actn_max+1)

    def __call__(self, *args, **kwargs):
        return self.brain()

class DirectOracle(Oracle):
    def __init__(self, env_type, *args, **kwargs):
        self.env_type = env_type

        if self.env_type == "numberline-v0":
            self.brain = zoom_solution
        else:
            raise NotImplemented

    def __call__(self, env, *args, **kwargs):
        """
        Args:
            env: SequentialEnvironment
                the environment
        """
        return self.brain(env.controller)

