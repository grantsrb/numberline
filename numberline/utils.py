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

def get_max_row(objs: set, min_row: int=None, ret_count: bool=False):
    """
    Finds the row in which the majority of objects reside. Returns the
    earliest row in case of equal counts.

    Args:
        objs: set of GameObjects
        min_row: int or None (inclusive)
            determines the minimum row available for counting. if None
            all rows are available.
        ret_count: bool
            if true, returns the count associated with the max row
    Returns:
        max_row: int
            the index of the row with the largest number of objects.
        count: int
            the count of the items along the max_row
    """
    rows, _ = get_row_and_col_counts(objs)
    if min_row is not None:
        for i in range(min_row):
            if i in rows: del rows[i]
    max_row = max_key(rows)
    if ret_count:
        if max_row in rows: return max_row, rows[max_row]
        else: return max_row, 0
    return max_row

def get_unaligned_items(items: set, targs: set, min_row: int=2):
    """
    Returns all items that are not aligned along the majority
    row and do not have a target in their column. Only one item
    for one target is allowed.

    Args:
        items: set of GameObjects
            the items in the register
        targs: set of GameObjects
            the targets in the register
        min_row: int
            the minimum row that is allowed to be the majority row. If
            items are below this row, they are automatically considered
            loners.
    Returns:
        loners: set of GameObjects
            the items that don't have a corresponding target in
            their column or do not align on the row with the
            maximum number of target aligned items
    """
    coord_counts = get_coord_counts(items)
    max_row = get_max_row(items, min_row=min_row)
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

def get_aligned_items(items: set, targs: set, min_row: int=1):
    """
    Returns all items that are aligned along the majority row and have
    a target in their column. Only one item for one target is allowed.

    Args:
        items: set of GameObjects
            the items in the register
        targs: set of GameObjects
            the targets in the register
        min_row: int
            the minimum row that is allowed to be the majority row. If
            items are below this row, they are automatically considered
            loners.
    Returns:
        aligneds: set of GameObjects
            the items that have a corresponding target in their column
            while sitting on the row with the maximum number of
            aligned items
    """
    loners = get_unaligned_items(
        items=items,
        targs=targs,
        min_row=min_row
    )
    return items-loners

def max_key(d):
    """
    Finds the maximum value of all the keys in the dict and returns
    the key.

    Args:
        d: dict
    Returns:
        k: key or None
            if no rows have any items, returns None
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

def coord_diff(coord0, coord1):
    """
    Returns the vector difference of coord0-coord1

    Args:
        coord1: sequence of ints (row, col)
        coord2: sequence of ints (row, col)
    Returns:
        diff: sequence of ints (row, col)
            coord0-coord1
    """
    return (coord0[0]-coord1[0], coord0[1]-coord1[1])

def coord_add(coord0, coord1):
    """
    Returns the vector addition of coord0+coord1

    Args:
        coord1: sequence of ints (row, col)
        coord2: sequence of ints (row, col)
    Returns:
        diff: sequence of ints (row, col)
            coord0+coord1
    """
    return (coord0[0]+coord1[0], coord0[1]+coord1[1])

def decompose(val, atoms):
    """
    Decomposes the argued value into the available atoms starting with
    the biggest atom and continuing down the line.. For example, if
    the atoms were [1,4,10] and the val was 7, the result would be
    {4: 1, 1: 3} There is one 4 and three ones to make 7.

    WARNING: in special circumstances it is possible to not get the
    fewest number of atoms. For example, if the atoms are [1,7,10] and
    the val is 14, this function will return one 10 and four 1s rather
    than two 7s.

    Args:
        val: int
        atoms: list of ints
    Returns:
        counts: dict
            This dict maps the values of the atoms to the quantity
            required to most efficiently represent the argued value.

            keys: int
                the value of the block
            vals: int
                the count of the block of this particular value
    """
    atoms = list(reversed(sorted(atoms)))
    counts = {atom: 0 for atom in atoms}
    remaining = int(val)
    for atom in atoms:
        if remaining <= 0 or atom <= 0: break
        count = remaining/atom
        if int(count) == count: remaining = 0
        else: remaining = remaining - int(count)*atom
        counts[atom] = int(count)
    return counts

def get_multiples_pairs(val):
    """
    Returns a list of all pairs of multiples of the argued value.
    (1,val) is always included in the list.

    Args:
        val: int
            must be positive real valued
    Returns:
        multiples: list of tuples of ints or None
            returns None if val is less than or equal to 0
    """
    if val <= 0: return None
    multiples = []
    for i in range(1, int(np.sqrt(val))+1):
        if val % i == 0: 
            multiples.append((i, val//i))
    return multiples

def widest_width(block_sizes):
    """
    Returns the width of the widest block.

    Args:
        block_sizes: dict
            keys: int
                the values of the blocks
            vals: tuple of ints (n_row, n_col)
                the sizes of the blocks
    Returns:
        widest_width: int
    """
    widest = -np.inf
    for size in block_sizes.values():
        if size[1] > widest:
            widest = size[1]
    return widest

def get_max_steps(targ_val):
    """
    Returns the maximum steps allowed in a given episode.

    Args:
        targ_val: float
    """
    sig_figs = get_sig_figs(targ_val)
    return 30

def get_sig_figs(num):
    """
    Returns the number of significant figures of the argued number.

    Args:
        num: float
    """
    raise NotImplemented
