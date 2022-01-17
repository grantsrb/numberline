import numpy as np
from mathblocks.blocks.utils import nearest_obj, euc_distance, get_unaligned_items, get_aligned_items, get_rows_and_cols, get_row_and_col_counts, get_max_row, decompose
from mathblocks.blocks.constants import *

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
        goal_coord = nearest_avail_drop(reg, max_row)
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

def nearest_avail_drop(reg, min_row=0):
    """
    Finds the position nearest to the player that allows the blocks
    to all be aligned from largest to smallest along a single row.

    Args:
        reg: Register
            reg.player must be holding a Block
        min_row: int or None
            the minimum row to being the search
    Returns:
        coord: tuple of ints
            the coord that can accommodate the block
    """
    if min_row is None: min_row = 0
    goal_coord = None
    remain_val = reg.targ_val-reg.block_sum
    remain_width = width_of_all_blocks(decompose(remain_val,BLOCK_VALS))
    blocks = {*reg.blocks}
    if reg.player.is_holding:
        remain_width += reg.player.held_obj.size[1]
        blocks = blocks - {reg.player.held_obj}
    if len(reg.blocks) > 1:
        furthest_col = furthest_right_empty_col(blocks)
        if furthest_col+remain_width < reg.grid.shape[1]:
            return (min_row,furthest_col)
        else:
            return find_avail_space(reg, min_row, 0)
    # Need to find nearest space to player that still allows all
    # blocks to be placed rightward within the grid
    else:
        col = reg.player.coord[1]
        loopcount = 0
        while reg.grid.shape[1]-col <= remain_width and loopcount < 1000:
            col -= 1
            loopcount += 1
        if col >= 0:
            return (min_row, col)
        return find_avail_space(reg, min_row, 0)

def find_avail_space(reg, min_row=0, min_col=0):
    """
    Simply searches from the min_col rightward along each row starting
    from min_row for the next available space that can accommodate the
    player and the object that the player is holding without overlapping
    with anything else.

    Args:
        reg: Register
            reg.player must be holding a Block
        min_row: int or None
            the minimum row to being the search
        min_col: int or None
            the minimum column to being the search
    Returns:
        coord: tuple of ints
            the coord that can accommodate the block. if None are
            available, returns (2,2)
    """
    if min_row is None: min_row = 0
    row = min_row-1
    loopcount = 0
    max_count = reg.grid.shape[0]*reg.grid.shape[1]
    goal_coord = None
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

def furthest_right_empty_col(objs):
    """
    Finds the earliest column that has no objs to the right of it.
    The size of the objects is factored into the calculations.

    Args:
        objs: set of GameObjects
    Returns:
        col: int
            the column that is just to the right of all argued
            gameobjects. 

            If len(objs) is 0, returns 0.
    """
    largest_col = 0
    for obj in objs:
        if obj.coord[1]+obj.size[1] > largest_col:
            largest_col = obj.coord[1]+obj.size[1]
    return largest_col

def width_of_all_blocks(block_counts, space_between=0):
    """
    Finds the sum of the width of all blocks in the counts.

    Args:
        block_counts: dict
            keys: int
                the potential values of the blocks
            vals: int
                the counts of that block type
        space_between: int
            any additional space you want to add between each block
    Returns:
        total_width: int
            the total width of all blocks plus the space between
    """
    total_width = 0
    for bv, count in block_counts.items():
        total_width += BLOCK_SIZES[bv][1]*count + space_between
    return total_width

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
            the block that should be removed from the grid. returns
            None if the block_sum is less than the targ_val as no blocks
            should be removed in this case.
    """
    if reg.targ_val > reg.block_sum: return None
    current_counts = reg.block_counts
    keys = reversed(sorted(BLOCK_VALS))
    removal_key = None
    running_sum = 0
    for k in keys:
        running_sum += k*current_counts[k]
        if running_sum > reg.targ_val:
            removal_key = k
            break
    candidates = set()
    for block in reg.blocks:
        if block.val == removal_key: candidates.add(block)
    return nearest_obj(reg.player, candidates)

