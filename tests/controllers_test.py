import mathblocks.blocks.controllers as controllers
from mathblocks.blocks.constants import DIRECTION2STR
from mathblocks.blocks.utils import get_multiples_pairs
from mathblocks.blocks.ai import direct_counter
import matplotlib.pyplot as plt

if __name__=="__main__":
    targ_range = (1,13)
    grid_size = (50,50)
    pixel_density=1
    max_num = 100
    contr = controllers.Controller(
        targ_range=targ_range,
        grid_size=grid_size,
        pixel_density=pixel_density,
        max_num=max_num
    )
    for i in range(10):
        obs = contr.reset()
        done = False
        count = 0
        while not done:
            print("looping", count)
            count += 1
            action = direct_counter(contr)
            obs, rew, done, info = contr.step(action)
            print("done: ", done)
            print("rew: ", rew)
            plt.imshow(obs)
            plt.show()

