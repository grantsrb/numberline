import numpy as np
from mathblocks.blocks.utils import nearest_obj, euc_distance, get_unaligned_items, get_aligned_items, get_rows_and_cols, get_row_and_col_counts, get_max_row, decompose
from mathblocks.blocks.constants import *

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

def find_empty_space_along_row(register, seed_coord):
    """
    Finds the nearest playable empty space along the row of the seed
    coordinate.

    Args:
        register: Register
        seed_coord: tuple of ints (row, col) in grid units
    Returns:
        coord:
            the nearest empty space along the seed row
    """
    grid = register.grid
    row, seed_col = seed_coord
    try_col = seed_col
    max_cols = register.grid.pixel_shape[1]
    count = -1
    while not register.is_empty((row,try_col)) and count < max_cols:
        count+=1
        half = count//2
        if count % 2 == 0: try_col = seed_col + half
        else: try_col = seed_col - half
    coord = (row,try_col)
    if not (grid.col_inbounds(try_col) and register.is_empty(coord)):
        return None
    return coord

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

def direct_counter(contr):
    """
    Directly solves for the controller's target value by grabbing and
    aligning the required blocks from largest block to smallest. 

    If the agent is holding a block that is out of order, it is simply
    moved to the nearest empty location and placed there.

    If a merge is possible, the agent completes the merge.
    """
    reg = contr.register
    remain_val = reg.targ_val-reg.block_sum

    min_row = 2
    max_row, n_aligned = get_max_row(
        reg.blocks,
        min_row=min_row,
        ret_count=True
    )
    if max_row is None: max_row = min_row
    # TAKE BLOCK TO SEMI-ORGANIZED POSITION
    if reg.player.is_holding and remain_val >= 0:
        goal_coord = nearest_avail_drop(
            reg,
            max_row,
            min_col=1
        )
    # GO TO PILE TO DELETE BLOCK
    elif reg.player.is_holding and remain_val < 0:
        goal_coord = reg.piles[PILE+str(reg.player.held_obj.val)].coord
    # GO TO BUTTON, UR DUHN BROH
    elif remain_val == 0: goal_coord = reg.button.coord
    # BLOCK REMOVAL CASE
    # In this case, we need to remove a block from the grid
    elif remain_val < 0: 
        goal_coord = get_removal_block(reg).coord
    else: # There must be remaining blocks to place
        counts = decompose(remain_val, BLOCK_VALS)
        for bv in reversed(sorted(BLOCK_VALS)):
            if counts[bv] > 0:
                goal_coord = reg.piles[PILE+str(bv)].coord
                break

    # Convert Goal Coordinate to Action
    if reg.player.coord == goal_coord:
        return GRAB # will drop or pickup as necessary
    direction = get_direction(reg.player.coord, goal_coord)
    return direction

def nearest_avail_drop(reg, min_row=None, min_col=None):
    """
    Finds the nearest position that the player can drop the object it
    is holding without overlapping with other objects

    Args:
        reg: Register
            reg.player must be holding a Block
        min_row: int or None
            the minimum row to being the search
        min_col: int or None
            the minimum column to being the search
    Returns:
        coord: tuple of ints
            the coord that can accommodate the block
    """
    if min_row is None: min_row = 0
    if min_col is None: min_col = 0
    goal_coord = None
    row = min_row-1
    loopcount = 0
    max_count = reg.grid.shape[0]*reg.grid.shape[1]
    while goal_coord is None and loopcount < max_count:
        loopcount += 1
        row += 1
        goal_coord = reg.avail_coord_on_row(
            reg.player.held_obj,
            row,
            min_col=min_col
        )
    if goal_coord is None: goal_coord = (2,2)
    return goal_coord

def get_removal_block(reg):
    """
    Finds the block to remove when the sum of all blocks exceeds the
    target value.

    The removal block is defined by the smallest block that pushes the
    total sum over the target value when adding all blocks from largest
    to smallest.

    Args:
        reg: Register
    Returns:
        block: Block
            the block that should be removed from the grid.
    """
    assert reg.targ_val > reg.block_sum
    current_counts = reg.block_counts()
    keys = reversed(sorted(BLOCK_VALS))
    removal_key = None
    running_sum = 0
    for k in keys:
        running_sum += k*current_counts[k]
        if running_sum > reg.targ_val:
            removal_key = k
            break
    candidates = set()
    for block in blocks:
        if block.val == removal_key: candidates.add(block)
    return nearest_obj(reg.player, candidates)

# def even_line_match(contr):
#     """
#     Takes a register and finds the optimal movement and grab action
#     for the state of the register.
# 
#     Args:
#         contr: Controller
#     Returns:
#         direction: int
#             a directional movement
#         grab: int
#             whether or not to grab
#     """
#     register = contr.register
#     player = register.player
#     items = register.items
#     targs = register.targs
#     # find items that are out of place
#     lost_items = get_unaligned_items(items, targs)
#     aligned_items = items-lost_items # set math
# 
#     # determine which object we should grab next
#     if len(items) == len(targs) and len(lost_items) == 0:
#         grab_obj = register.button
#     elif len(lost_items) > 0:
#         grab_obj = nearest_obj(player, lost_items)
#     else:
#         grab_obj = register.pile
# 
#     # if on top of grab_obj, grab it, otherwise don't
#     if grab_obj.coord == player.coord: grab = True
#     else: grab = False
# 
#     # determine where to move next
#     if not grab: goal_coord = grab_obj.coord
#     # If we're on top of the button, simply issue a STAY order
#     elif grab_obj == register.button: return STAY, grab
#     elif len(items) > len(targs):
#         goal_coord = register.pile.coord
#     # Need to find nearest target that has not been completed and
#     # find the appropriate coord for placing an item to complete it
#     else:
#         try:
#             goal_coord = get_even_line_goal_coord(
#                 player,
#                 aligned_items,
#                 targs,
#                 register.grid.middle_row
#             )
#         except:
#             print("lost items")
#             print(lost_items)
#             print("aligned items")
#             print(aligned_items)
#             print("grab_obj")
#             print(grab_obj)
#             print("items")
#             print(items)
#             print("targs")
#             print(targs)
# 
#     direction = get_direction(player.coord, goal_coord)
#     return direction, grab
# 
# def cluster_match(contr):
#     """
#     Takes a register and finds the optimal movement and grab action
#     for the state of the register in the cluster match game. Also works
#     for cluster cluster match and orthogonal line match.
# 
#     Args:
#         contr: Controller
#     Returns:
#         direction: int
#             a directional movement
#         grab: int
#             whether or not to grab
#     """
#     register = contr.register
#     player = register.player
#     items = register.items
#     n_targs = register.n_targs
# 
#     min_row = 2
#     max_row, n_aligned = get_max_row(
#         items,
#         min_row=min_row,
#         ret_count=True
#     )
#     unaligned = set(filter(lambda x: x.coord[0]!=max_row, items))
#     # check if two objects are ontop of eachother (excluding player)
#     is_overlapping = register.is_overlapped(player.coord)
#     if is_overlapping:
#         grab_obj = nearest_obj(player, items)
#     elif n_aligned == n_targs and len(unaligned) == 0:
#         grab_obj = register.button
#     elif len(unaligned)>0:
#         grab_obj = nearest_obj(player, unaligned)
#     else:
#         grab_obj = register.pile
# 
#     if player.coord==grab_obj.coord: grab = True
#     else: grab = False
# 
#     if not grab:
#         goal_coord = grab_obj.coord
#     else: # Either on pile or unaligned object
#         goal_row = max_row if max_row is not None else 2
#         temp_col = register.grid.shape[1]//2
#         seed_coord = (goal_row, player.coord[1])
#         goal_coord = find_empty_space_along_row(
#             register=register,
#             seed_coord=seed_coord
#         )
#         if goal_coord is None:
#             goal_coord = register.button.coord
#             if player.coord == goal_coord: grab = True
#             print("Goal coord was None for seed_coord:", seed_coord)
#             print("Item count: ", register.n_items)
#             print("Targ count: ", register.n_targs)
#     direction = get_direction(player.coord, goal_coord)
#     return direction, grab
# 
# def rev_cluster_match(contr):
#     """
#     Takes a register and finds the optimal movement and grab action
#     for the state of the register in the reverse cluster match game.
# 
#     Args:
#         contr: Controller
#     Returns:
#         direction: int
#             a directional movement
#         grab: int
#             whether or not to grab
#     """
#     register = contr.register
#     player = register.player
#     items = register.items
#     targs = register.targs
#     
#     # used later to determine if all items are aligned
#     aligned_items = get_aligned_items(items, targs, min_row=0)
# 
#     # check if two objects are ontop of eachother (excluding player)
#     is_overlapping = register.is_overlapped(player.coord)
#     if len(items) == len(targs) and not is_overlapping:
#         if len(targs) == 1 or len(aligned_items)!=len(targs):
#             grab_obj = register.button # hard work done
#         else: # len(aligned_items) == len(targs)
#             # need to unalign an item
#             grab_obj = nearest_obj(player, aligned_items)
#     elif len(items) >= len(targs) or is_overlapping:
#         grab_obj = nearest_obj(player, items) # grab existing item
#     else:
#         grab_obj = register.pile
# 
#     # if on top of grab_obj, grab it, otherwise don't
#     if grab_obj.coord == player.coord: grab = True
#     else: grab = False
# 
#     # determine where to move next
#     if not grab: goal_coord = grab_obj.coord
#     # If we're on top of the button, simply issue a STAY order and grab
#     elif grab_obj == register.button: return STAY, grab
#     elif len(items) > len(targs):
#         goal_coord = register.pile.coord
#     # Here we know that we have an item in our grasp. if we're in an
#     # empty space, we can simply drop it. And that will have already
#     # been done in the logic above. We can just search for the nearest
#     # empty space centered on the pile.
#     else:
#         goal_coord = register.find_space(register.pile.coord)
#     direction = get_direction(player.coord, goal_coord)
#     return direction, grab
# 
