# Math Blocks

## Description
Math blocks is a game in which simple arithmetic mathematical questions are posed and answered visually. The objects within the game consist of rectangles of varying sizes and colors. Each size-color combination is meant to represent one of the numbers 1, 5, 10, 50, 100, or 500. The agent has the ability to create new blocks and stack existing blocks to convert them to a larger block size.

Questions are posed visually at the bottom of the screen using a group of blocks A and another group of blocks B with a symbol between them representing addition, multiplication, or subtraction (negative solutions are not allowed). The agent must produce the appropriate representative quantity using the counting blocks to solve the equation. Once the agent believes it has found the solution, it presses a button to end the game.

## Dependencies
- python3
- pip
- gym
- numpy
- matplotlib

## Installation
1. Clone this repository
2. Navigate to the cloned repository
3. Run command `$ pip install -e ./`
4. add `import mathblocks` to the top of your python script
5. make one of the envs with the folowing: `env = gym.make("mathblocks-<version here>")`

## Rendering
A common error about matplotlib using `agg` can be fixed by including the following lines in your scripts before calling `.render()`:

    import matplotlib
    matplotlib.use('TkAgg')

If you are experiencing trouble using the `render()` function while using jupyter notebook, insert:

    %matplotlib notebook

before calling `render()`.

## Rewards
A negative reward representing the squared error between the appropriate numerical representation of the solution and the agent's actual numerical representation of the solution to the visual equation.

## Game Options

- _grid_size_: An row,col coordinate denoting the number of units on the grid (height, width).
- _pixel_density_: Number of numpy pixels within a single grid unit.
- _targ_range_: A range of possible target solution counts for each game (inclusive). The maximum must be less than half of the area of the grid.

Each of these options are member variables of the environment and will come into effect after the environment is reset. For example, if you wanted to use 1-5 targets in game A, you can be set this using the following code:

    env = gym.snake('gordongames-v0')
    env.targ_range = (1,5)
    observation = env.reset()

## Code Details
### Grid
The grid handles creating the canvas for the game. It handles any interface with the actual image being produced by the game. Use it to draw blocks to the image. Coordinates are drawn using a (Row,Col) coordinate system in which row indexes start at the top of the image just like an array. For example, the upper leftmost pixel is (0,0) and the lower right most pixel is (NRows-1, NCols-1). The upper-most row of the image and two colums in from the left would correspond to (0,1).

### GameObject
Each visual on the screen is defined by a GameObject object. It holds the type of object, the corresponding color, and the corresponding shape.

#### GameObject Types:
- Player: an object to represent the player's location
- Operator: an object to represent a mathematical operation
- Button: an object that is pressed when the player wishes to end the episode
- Block1: a block representing 1 unit
- Block5: a block representing 5 units
- Block10: a block representing 10 units
- Block50: a block representing 50 units
- Block100: a block representing 100 units
- Block500: a block representing 500 units
- Block1Pile: an object representing the location to create a new block representing 1 unit
- Block5Pile: an object representing the location to create a new block representing 5 units
- Block10Pile: an object representing the location to create a new block representing 10 units
- Block50Pile: an object representing the location to create a new block representing 50 units
- Block100Pile: an object representing the location to create a new block representing 100 units
- Block500Pile: an object representing the location to create a new block representing 500 units

### Register
The register tracks and updates all GameObjects and their locations. The register holds a dict mapping coordinates to a list of any residing GameObjects as well as a set that contains all GameObjects and a set for each type of GameObject that holds all of the corresponding objects. The register is used to translate, add, and remove all GameObjects from the game. The Register also holds a function to update the grid with the current state of all GameObjects. The register also handles coversions between different types of blocks. Conversions automatically occur when possible.

### Controller
Controllers handle all game logic. They handle initializing objects and any logic for moving objects and any reward functions for agent success.

