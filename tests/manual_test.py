import numberline
from numberline.constants import *
import gym

if __name__=="__main__":
    args = {
        "unit_density": 3,
        "targ_range": (1,13),
        "operators": {ADD, SUBTRACT},
    }
    env = gym.make("numberline-v0", **args)

    done = False
    rew = 0
    obs = env.reset()
    env.render()
    key = ""
    action = "w"
    while key != "q":
        key = input("action: ")
        if key   == "w": action = ACTION2IDX[ZOOM_IN]
        elif key == "d": action = ACTION2IDX[RIGHT]
        elif key == "s": action = ACTION2IDX[ZOOM_OUT]
        elif key == "a": action = ACTION2IDX[LEFT]
        elif key == "f": action = ACTION2IDX[ADD_ONE]
        elif key == "c": action = ACTION2IDX[SUBTRACT_ONE]
        elif key == "r": action = ACTION2IDX[END_GAME]
        obs, rew, done, info = env.step(action)
        print("rew:", rew)
        print("done:", done)
        print("info")
        for key in info.keys():
            print("    ", key, ": ", info[key])
        if done:
            obs = env.reset()
        env.render()
