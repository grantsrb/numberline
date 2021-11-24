import numpy as np
from collections import defaultdict

def get_rows_and_cols(objs: set):
    """
    Finds and returns sets of the row and column values of the
    argued set of objects.

    Args:
        objs: set of GameObjects
    Returns:
        rows: set of ints
            a set of the row values
        cols: set of ints
            a set of the column values
    """
    rows, cols = get_row_and_col_counts(objs)
    return set(rows.keys()), set(cols.keys())

def get_row_and_col_counts(objs: set):
    """
    Finds and returns dicts of the row and column values and their
    corresponding counts.

    Args:
        objs: set of GameObjects
    Returns:
        rows: dict
            keys: int
                the row values
            vals: int
                the number of objects with that row value
        cols: dict
            keys: int
                the col values
            vals: int
                the number of objects with that col value
    """
    rows = dict()
    cols = dict()
    for obj in objs:
        row,col = obj.coord
        if row not in rows: rows[row] = 1
        else: rows[row] += 1
        if col not in cols: cols[col] = 1
        else: cols[col] += 1
    return rows, cols

def get_coord_counts(objs: set):
    """
    Counts the number of occurences of the coordinates each object
    within the sequence.

    Args:
        objs: list like of GameObjects
    Returns:
        counts: dict
            keys: coord tuples
                the coordinates
            vals: int
                the counts
    """
    counts = defaultdict(lambda: 0)
    for obj in objs:
        counts[obj.coord] += 1
    return counts

def get_unaligned_items(items: set, targs: set, min_row: int=2):
    """
    Returns all items that are not aligned along the majority
    row and do not have a target in their column. Only one item
    for one target is allowed.

    Returns:
        loners: set of GameObjects
            the items that don't have a corresponding target in
            their column or do not align on the row with the
            maximum number of target aligned items
    """
    coord_counts = get_coord_counts(items)
    item_rows, _ = get_row_and_col_counts(items)
    if min_row is not None:
        for i in range(min_row):
            if i in item_rows: del item_rows[i]
    max_row = max_key(item_rows)
    _, targ_cols = get_rows_and_cols(targs)

    loners = set()
    for item in items:
        if item.coord[1] not in targ_cols:
            loners.add(item)
        elif item.coord[0] != max_row:
            loners.add(item)
        elif coord_counts[item.coord] > 1:
            coord_counts[item.coord] -= 1
            loners.add(item)
    return loners

def max_key(d):
    """
    Finds the maximum value of all the keys in the dict and returns
    the key.

    Args:
        d: dict
    Returns:
        k: key
    """
    max_count = 0
    m_key = None
    for k,v in d.items():
        if v > max_count: m_key = k
    return m_key

def nearest_obj(ref_obj, objs):
    """
    Searches through the objs set for the nearest object to the
    ref_obj.

    Args:
        ref_obj: GameObject
        objs: set or list of GameObjects
    Returns:
        nearest: GameObject
            the closest object to the ref_obj
    """
    ref_coord = np.asarray(ref_obj.coord)
    min_dist = np.inf
    nearest = None
    for obj in objs:
        dist = np.linalg.norm(ref_coord - np.asarray(obj.coord))
        if dist < min_dist:
            min_dist = dist
            nearest = obj
    return nearest

def euc_distance(coord1, coord2):
    """
    Finds the euclidian distance between two coordinates.

    Args:
        coord1: sequence of ints (row, col)
        coord2: sequence of ints (row, col)
    Returns:
        dist: float
    """
    return np.linalg.norm(np.asarray(coord1) - np.asarray(coord2))

