import numpy as np
from gordongames.envs.ggames.utils import nearest_obj, euc_distance, get_unaligned_items, get_aligned_items, get_rows_and_cols, get_row_and_col_counts
from gordongames.envs.ggames.constants import *

def get_even_line_goal_coord(player: object,
                             aligned_items: set,
                             targs: set,
                             max_row: int):
    """
    Finds the row and col of the goal. If no row is established, it
    arbitrarily picks row 2. Assumes len(aligned_items) <= len(targs)

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

    Args:
        contr: Controller
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
    aligned_items = items-lost_items # set math

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
    elif len(items) > len(targs):
        goal_coord = register.pile.coord
    # Need to find nearest target that has not been completed and
    # find the appropriate coord for placing an item to complete it
    else:
        try:
            goal_coord = get_even_line_goal_coord(
                player,
                aligned_items,
                targs,
                register.grid.middle_row
            )
        except:
            print("lost items")
            print(lost_items)
            print("aligned items")
            print(aligned_items)
            print("grab_obj")
            print(grab_obj)
            print("items")
            print(items)
            print("targs")
            print(targs)

    direction = get_direction(player.coord, goal_coord)
    return direction, grab

def cluster_match(contr):
    """
    Takes a register and finds the optimal movement and grab action
    for the state of the register in the cluster match game.

    Args:
        contr: Controller
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
    
    # used later to determine if all items are aligned
    aligned_items = get_aligned_items(items, targs, min_row=0)

    is_overlapping = register.is_overlapped(player.coord)
    if len(items) == len(targs) and not is_overlapping:
        if len(targs) == 1 or len(aligned_items)!=len(targs):
            grab_obj = register.button # hard work done
        else: # len(aligned_items) == len(targs)
            # need to unalign an item
            grab_obj = nearest_obj(player, aligned_items)
    elif len(items) >= len(targs):
        grab_obj = nearest_obj(player, items) # grab existing item
    elif is_overlapping:
        grab_obj = nearest_obj(player, items)
    else:
        grab_obj = register.pile

    # if on top of grab_obj, grab it, otherwise don't
    if grab_obj.coord == player.coord: grab = True
    else: grab = False

    # determine where to move next
    if not grab: goal_coord = grab_obj.coord
    # If we're on top of the button, simply issue a STAY order and grab
    elif grab_obj == register.button: return STAY, grab
    elif len(items) > len(targs):
        goal_coord = register.pile.coord
    # Here we know that we have an item in our grasp. if we're in an
    # empty space, we can simply drop it. And that will have already
    # been done in the logic above. We can just search for the nearest
    # empty space centered on the pile.
    else:
        goal_coord = register.find_space(register.pile.coord)
    direction = get_direction(player.coord, goal_coord)
    return direction, grab

