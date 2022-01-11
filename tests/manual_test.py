import mathblocks
from mathblocks.blocks.constants import *
import gym

if __name__=="__main__":
    args = {
        "grid_size": (50,50),
        "pixel_density": 1,
        "targ_range": (1,13),
        "max_num": 100,
    }
    env = gym.make("mathblocks-v0", **args)

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
        elif key == "c": action = 6
        obs, rew, done, info = env.step(action)
        print("rew:", rew)
        print("done:", done)
        print("info")
        for key in info.keys():
            print("    ", key, ": ", info[key])
        if done:
            obs = env.reset()
        env.render()
