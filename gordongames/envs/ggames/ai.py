import numpy as np
from gordongames.envs.ggames.utils import nearest_obj, euc_distance, get_unaligned_items, get_rows_and_cols, get_row_and_col_counts
from gordongames.envs.ggames.constants import *

def get_even_line_goal_coord(player: object,
                             aligned_items: set,
                             targs: set,
                             max_row: int):
    """
    Finds the row and col of the goal. If no row is established, it
    picks row 2.

    Args:
        player: GameObject
            the player object
        aligned_items: set of GameObjects
            a set of all the items that are in their final state or
            are at least aligned on the goal row
        targs: set of GameObjects
            a set of all the targs in the game
        max_row: int (exclusive)
            the maximum allowed row if the item row has not yet been
            established. 
    Returns:
        goal_coord: tuple (row, col)
            the coordinate that the player should move towards
    """
    loners = get_unaligned_items(targs, aligned_items)
    goal_targ = nearest_obj(player, loners)
    goal_row = 2
    if len(aligned_items) > 0:
        goal_row = next(iter(aligned_items)).coord[0]
    return (goal_row, goal_targ.coord[1])

def get_direction(coord0, coord1):
    """
    Finds the movement direction from coord0 to coord1.

    Args:
        coord0: tuple (row, col) in grid units
            the coordinate that we will be moving from
        coord1: tuple (row, col) in grid units
            the coordinate that we will be moving to
    Returns:
        direction: int [0, 1, 2, 3, 4]
          The direction to move closer to coord1 from coord0.
          Check DIRECTIONS to ensure these values haven't changed
              0: no movement
              1: move up (lower row unit)
              2: move right (higher column unit)
              3: move down (higher row unit)
              4: move left (lower column unit)
    """
    start_row, start_col = coord0
    end_row, end_col = coord1
    row_diff = int(end_row - start_row)
    col_diff = int(end_col - start_col)
    if row_diff != 0 and col_diff != 0:
        if np.random.random() < .5:
            return DOWN if row_diff > 0 else UP
        else:
            return RIGHT if col_diff > 0 else LEFT
    elif row_diff != 0:
        return DOWN if row_diff > 0 else UP
    elif col_diff != 0:
        return RIGHT if col_diff > 0 else LEFT
    else:
        return STAY

def even_line_match(contr):
    """
    Takes a register and finds the optimal movement and grab action
    for the state of the register.

    Returns:
        direction: int
            a directional movement
        grab: int
            whether or not to grab
    """
    register = contr.register
    player = register.player
    items = register.items
    targs = register.targs
    # find items that are out of place
    lost_items = get_unaligned_items(items, targs)
    aligned_items = items-lost_items

    # determine which object we should grab next
    if len(items) == len(targs) and len(lost_items) == 0:
        grab_obj = register.button
    elif len(lost_items) > 0:
        grab_obj = nearest_obj(player, lost_items)
    else:
        grab_obj = register.pile

    # if on top of grab_obj, grab it, otherwise don't
    if grab_obj.coord == player.coord: grab = True
    else: grab = False

    # determine where to move next
    if not grab: goal_coord = grab_obj.coord
    # If we're on top of the button, simply issue a STAY order
    elif grab_obj == register.button: return STAY, grab
    # Need to find nearest target that has not been completed and
    # find the appropriate coord for placing an item to complete it
    else:
        goal_coord = get_even_line_goal_coord(
            player,
            aligned_items,
            targs,
            register.grid.middle_row
        )
    direction = get_direction(player.coord, goal_coord)
    return direction, grab

