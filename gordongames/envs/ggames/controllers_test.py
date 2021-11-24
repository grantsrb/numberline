import controllers
import matplotlib.pyplot as plt
from ai import even_line_match

if __name__=="__main__":
    targ_range = (1,5)
    grid_size = (15,15)
    pixel_density=4
    harsh=True
    contr = controllers.EvenLineMatchController(
        targ_range=targ_range,
        grid_size=grid_size,
        pixel_density=pixel_density,
        harsh=harsh
    )
    for i in range(10):
        contr.harsh = not contr.harsh
        obs = contr.reset()
        done = False
        while not done:
            direction, grab = even_line_match(contr)
            obs, rew, info, done = contr.step(direction, grab)
            print("done: ", done)
            print("rew: ", rew)
            plt.imshow(obs)
            plt.show()

