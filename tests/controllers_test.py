import numberline.controllers as controllers
from   numberline.constants import *
from   numberline.ai import zoom_solution
import matplotlib.pyplot as plt

if __name__=="__main__":
    kwargs = {
        "pixel_density": 3,
        "targ_range": (-123,123),
        "operators": {ADD, SUBTRACT},
    }
    contr = controllers.Controller(
        **kwargs
    )
    for i in range(100):
        obs = contr.reset()
        done = False
        count = 0
        while not done:
            print("looping", count)
            count += 1
            action = zoom_solution(contr)
            print("actn:", IDX2ACTION[action])
            obs, rew, done, info = contr.step(action)
            print("done: ", done)
            print("rew: ", rew)
            print("info:", info)
            plt.imshow(obs)
            plt.show()

