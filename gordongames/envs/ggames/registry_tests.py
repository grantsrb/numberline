from grid import Grid
from registry import Register
import matplotlib.pyplot as plt
from constants import PLAYER, TARG, PILE, ITEM, DIVIDER, BUTTON, OBJECT_TYPES, STAY, UP, RIGHT, DOWN, LEFT, DIRECTIONS, COLORS, EVENTS, STEP, BUTTON, FULL, DEFAULT
import numpy as np

if __name__ == "__main__":
    grid = Grid((15,31), 10, divide=True)
    register = Register(grid, n_targs=3)
    for i in range(10):
        register.line_match()
        register.reset()
        for targ in register.targs:
            print(targ.prev_coord, targ.coord)
        for move in [UP, RIGHT, RIGHT, DOWN, DOWN, DOWN, LEFT, LEFT, LEFT, UP]:
            register.step(move, 0)
            plt.imshow(register.grid.grid)
            plt.show()

    grid.reset()
    register = Register(grid, n_targs=7)
    for i in range(10):
        register.line_match()
        register.reset()
        plt.imshow(register.grid.grid)
        plt.show()

    grid.reset()
    register = Register(grid, n_targs=25)
    for i in range(10):
        register.line_match()
        register.reset()
        plt.imshow(register.grid.grid)
        plt.show()

    print("uneven")
    grid.reset()
    register = Register(grid, n_targs=3)
    for i in range(10):
        register.uneven_line_match()
        register.reset()
        plt.imshow(register.grid.grid)
        plt.show()

    grid.reset()
    register = Register(grid, n_targs=7)
    for i in range(10):
        register.uneven_line_match()
        register.reset()
        plt.imshow(register.grid.grid)
        plt.show()

    grid.reset()
    register = Register(grid, n_targs=25)
    for i in range(10):
        register.uneven_line_match()
        register.reset()
        plt.imshow(register.grid.grid)
        plt.show()
