import gordongames
from gordongames.envs.ggames.constants import *
import gym

if __name__=="__main__":
    args = {
        "grid_size": (9,9),
        "pixel_density": 1,
        "targ_range": (1,4),
        "harsh": False,
    }
    env = gym.make("gordongames-v0", **args)

    done = False
    rew = 0
    obs = env.reset()
    env.render()
    key = ""
    action = "w"
    while key != "q":
        key = input("action: ")
        if key   == "w": action = UP
        elif key == "d": action = RIGHT
        elif key == "s": action = DOWN
        elif key == "a": action = LEFT
        elif key == "f": action = 5
        obs, rew, done, info = env.step(action)
        print("rew:", rew)
        print("done:", done)
        if done:
            obs = env.reset()
        env.render()
