# gordongames

## Description
gordongames is a gym environment for recreating computational versions of games proposed in Peter Gordon's paper [_Numerical Cognition Without Words: Evidence from Amazonia_](https://www.science.org/doi/10.1126/science.1094492). 

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
4. add `import gordongames` to the top of your python script
5. make one of the envs with the folowing: `env = gym.make("gordongames-<version here>")`

## Rendering
If you are experiencing trouble using the `render()` function while using jupyter notebook, insert:

    %matplotlib notebook

before calling `render()`.

## Using gordongames
After installation, you can use gordongames by making one of the gym environments. See the paper [_Numerical Cognition Without Words: Evidence from Amazonia_](https://www.science.org/doi/10.1126/science.1094492) for more details about each game.

#### Environment A
Use `gym.make('gordongames-A')` to create the Line Match game. The agent must match the number of target objects by aligning them within the target columns. Targets are evenly spaced. These are the default options for the game (see Game Details to understand what each variable does):

    grid_size = [33,33]
    pixel_density = 1
    targ_range = (1,10)

#### Environment B
Use `gym.make('gordongames-B')` to create the Cluster Line Match game. The agent must match the number of target objects without aligning them. These are the default options for the game (see Game Details to understand what each variable does):

    grid_size = [33,33]
    pixel_density = 1
    targ_range = (1,10)

#### Environment C
Use `gym.make('gordongames-C')` to create the Orthogonal Line Match game. The agent must match the number of target objects aligning them along a single column. These are the default options for the game (see Game Details to understand what each variable does):

    grid_size = [33,33]
    pixel_density = 1
    targ_range = (1,10)

#### Environment D
Use `gym.make('gordongames-D')` to create the Uneven Line Match game. The agent must match the target objects by aligning them along each respective target column. The targets are unevenly spaced. These are the default options for the game (see Game Details to understand what each variable does):

    grid_size = [33,33]
    pixel_density = 1
    targ_range = (1,10)

#### Environment G
Use `gym.make('gordongames-G')` to create the Nuts-In-Can game. The agent watches a number of target objects get placed into a pile. The agent must then remove the correct number of objects. These are the default options for the game (see Game Details to understand what each variable does):

    grid_size = [33,33]
    pixel_density = 1
    targ_range = (1,10)


## Game Details
Each game consists of a randomly intitialized grid with various objects distributed on the grid depending on the game type. The goal is for the agent to first complete some task and then press the end button located in the upper right corner of the grid. Episodes last until the agent presses the end button. The agent can move left, up, right, down, or stay still. The agent also has the ability to interact with objects via the grab action. Grab only acts on objects in the same square as the agent. If the object is an "item", the agent carries the item to wherever it moves on that step. If the object is a "pile", a new item is created and carried with the agent for that step. The ending button is pressed using the grab action. The reward is only granted at the end of each episode if the task was completed successfully.

#### Rewards
A +1 reward is returned only in the event of a successful completion of the task.

A -1 reward is returned when a task ends unsuccessfully.

##### Environment A
The agent receives a +1 reward if each target has a single item located in its column at the end of the episode.

##### Environment B
The agent receives a +1 reward if there exists a single item for each target. Alignment is not considered.

##### Environment C
The agent receives a +1 reward if there exists an item for each target. All items must be aligned along a single column.

##### Environment D
The agent receives a +1 reward if each target has a single item located in its column at the end of the episode.

##### Environment G
The agent receives a +1 reward if the agent removes the exact number of items placed in the pile.


#### Game Options

- _grid_size_ - An row,col coordinate denoting the number of units on the grid (height, width).
- _pixel_density_ - Number of numpy pixels within a single grid unit.
- _targ_range_ - A range of possible initial target object counts for each game (inclusive). Must be less than `grid_size`. 

Each of these options are member variables of the environment and will come into effect after the environment is reset. For example, if you wanted to use 1-5 targets in game A, you can be set this using the following code:

    env = gym.snake('gordongames-A')
    env.targ_range = (1,5)
    observation = env.reset()


#### Environment Parameter Examples
Examples coming soon!

#### About the Code
Coming soon!
