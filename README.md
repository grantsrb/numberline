# Zooming Number Line

## Description
`numberline` is a game that is built to help artificial agents understand number as a one dimensional spatial quantity. The game consists of a single dimensional series of units with marks at every 10 units. The units fill up with color from left to right to represent numeric quantities. The goal of the game is to complete mathematical manipulations to the numberline as indicated by special, meta units (at the very end of the numberline).

The game has the ability to zoom in and out and translate its visual field left and right along the number line. The game also provides the ability to increase and decrease the filling in increments of 1 unit. The numeric value of the unit depends on the zoom level of the game. For example, if the game's zoom level is 1, units each represent 10 integers. If the game's zoom level is 0, each unit represents 1 integer. At a zoom of -1 each unit represents 0.1 values. The game has the ability to zoom infinitely inward and infinitely outward.

The observations consist of a single row of 105 units.

The first 101 indices (the image is 0 indexed where index 0 is the first unit and 104 represents the last unit in the image) are meant to represent values on the numberline. The Zero unit has a special color to orient the user to its location when in view. When the game starts, the zero unit is located at index 0.

The unit that exists at index 101 always indicates the zoom level as a floating point number. A zoom level of 0 represents the numberline from 0-100. A zoom level of -1 means units have a value of 0.1 and a zoom of 1 means units have a value of 10, etc. The zoom level is divided by `numberline.constants.ZOOM_DIVISOR` for a pixel value.

The unit at index 102 indicates a mathematical operation. Each operation is represented as a unit value. See `numberline.constants` for the raw values. Potential operations are ADD, SUBTRACT, MULTIPLY, and DIVIDE.

The unit at index 103 indicates the operand for the game (the number to combine the operator and the value of the numberline with). For example, if the numberline was empty, the operator was ADD, and the operand had a value of 3, then the goal would be to add 3 values to the number line. If the operator was MULTIPLY and the operator number was 3.14, the goal would then be to multiply the current state of the numberline by 3.14.

The unit at index 104 indicates the number of grid units that the center of the image is away from the special 0 point on the numberline. This is referred to as the translation. For example, when the numberline has a zoom of 0 and a translation of 50, then it is displaying values from 0-100. If the zoom level was -1 and the translation was 5, then the value at the center of the image would be 0.5.

The agent must perform a special ending action to indicate that it thinks it has filled the numberline appropriately.

When creating a new instance of the game, you can choose the minimum and maximum numberline numbers, the minimum and maximum operator numbers, the types of operators you would like to allow, whether you want the game to perpetuate the state of the numberline across episodes, and you can place limits on zooming and scrolling if you wish (so that an agent doesn't lose itself to the abyss).

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
A +1 reward is granted when the agent successfully completes an operation.

## Game Options

### Initial Settings
At the time of creation, the game allows for a variety of initial settings.

- pixel\_density (int): Number of numpy pixels making up the length and width of a single grid unit.
- init\_range (tuple of ints): A range of possible initial numberline values for each game (inclusive). defaults to (0,0). Only used once if `ep_reset` is true.
- targ\_range (tuple of ints): A range of possible target solution counts for each game (inclusive). defaults to (1,100)
- operators (list or set of str): the operators you would like to include in the game. The available arguments are contained in `numberline.constants.OPERATORS`
- is\_discrete (bool): indicates if the operator and target number ranges should be discrete or continuous. true means numbers are discrete. defaults to True
- zoom\_range (tuple of inclusive floats | None): indicates if the zoom should be restricted to finite amounts. 0 is a zoom level in which each unit represents a value of 1. A zoom of 1 is a level in which each unit represents 10. A zoom of -1 has each unit represent 0.1. Pixel values are set to the zoom level divided by `numberline.constants.ZOOM_DIVISOR`. defaults to None
- scroll\_range (tuple of inclusive ints | None): if None, no limits are set on the ability to scroll left and right. Otherwise the argued integers represent the min and maximum scrollable values on the numberline. defaults to None
- ep\_reset (bool): if true, the value of the numberline resets after each episode. If false the value of the numberline persists through episodes. defaults to True.

Each of these options are member variables of the environment and they can be changed between episodes. The recommended way to set these values, however, is as keyword arguements following the environment name at the time of creation. For example:

    kwargs = {
        "targ_range": (-100, 100),
        "op_range": (-100, 100),
        "ep_reset": False
    }
    env = gym.make('numberline-v0', **kwargs)
    observation = env.reset()

### Reset Keywords
You can also argue keyword arguments to the `env.reset()` function to set values for the start of the next episode. For example, argue `num_line=your_value` to set the initial state of the numberline. The example in code:

    observation = env.reset(num_line=10)

Here is a list of possible arguments:
- num\_line (int): the value that the numberline should start with.
- targ\_val (int): the value that the target value should be.
- op\_val (int): the value that the operator number should be.
- operator (str): the value that the operator should be


