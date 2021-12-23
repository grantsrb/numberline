import gordongames
import gym
from gordongames.envs.ggames.ai import even_line_match, cluster_match
from gordongames.envs.ggames.constants import DIRECTION2STR

class GordonOracle:
    def __init__(self, env_type, *args, **kwargs):
        self.env_type = env_type
        self.is_grabbing = False
        
        if self.env_type == "gordongames-v0":
            self.brain = even_line_match
        elif self.env_type == "gordongames-v1":
            self.brain = cluster_match
        else:
            raise NotImplemented

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

if __name__=="__main__":
    kwargs = {
        "targ_range": (1,13),
        "grid_size": (15,15),
        "pixel_density": 4,
        "harsh": True,
    }
    env_name = "gordongames-v1"
    env = gym.make(env_name, **kwargs)
    oracle = GordonOracle(env_name)
    for i in range(10):
        obs = env.reset()
        done = False
        while not done:
            actn = oracle(env)
            if actn < 5:
                print("actn:", DIRECTION2STR[actn])
            else:
                print("actn: GRAB")
            obs, rew, done, info = env.step(actn)
            print("done: ", done)
            print("rew: ", rew)
            env.render()

