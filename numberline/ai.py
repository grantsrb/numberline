import numpy as np
from numberline.constants import *
from numberline.utils import get_magnitude_counts


def zoom_solution(contr):
    """
    This function solves the numberline task by using the zoom and
    translation features of the game to do the minimal number of
    filling actions while always keeping filling actions within view.

    For example, if the target value of the numberline is 123.45, the
    agent would take the following steps. The agent will first zoom out
    to a zoom of 2. Next it would add one unit to the fill and then
    translate one unit to the right so that the view would be centered
    on the hundred's place in which the current fill is residing at.
    Next it would zoom in one level (1) and then add one unit to the
    fill (bringing the total fill value up to 110), translate to the
    right one unit (centering on the 110th value from the zero point on
    the numberline), and then repeat the last 2 actions to bring the
    fill to 120 and have the view centered on the edge of the fill. Next
    it would zoom in and repeat these steps till finally the zoom was
    at -2, the fill was at 123.45, and the translation was centered on
    the last unit of the fill.

    Args:
        contr: Controller
            the game controller
    """
    reg = contr.register
    remain_val = contr.targ_val-reg.fill
    if remain_val == 0: return ACTION2IDX[END_GAME]
    fill_trans = reg.val2unit(reg.fill)
    if reg.trans != fill_trans:
        trans_diff = fill_trans - reg.trans
        # If diff is magnitudes greater, zoom out
        if np.abs(trans_diff) > 10:
            fill_counts = get_magnitude_counts(trans_diff)
            mags = sorted(list(fill_counts.keys()), key=lambda x: -x)
            if reg.zoom > mags[0]:
                return ACTION2IDX[ZOOM_IN]
            elif reg.zoom < mags[0]: 
                return ACTION2IDX[ZOOM_OUT]
        elif trans_diff > 0:
            return ACTION2IDX[RIGHT]
        elif trans_diff < 0:
            return ACTION2IDX[LEFT]

    mag_counts = get_magnitude_counts(remain_val)
    # Descending remaining magnitude components
    mags = sorted(list(mag_counts.keys()), key=lambda x: -x)
    if reg.zoom > mags[0]:
        return ACTION2IDX[ZOOM_IN]
    elif reg.zoom < mags[0]: 
        return ACTION2IDX[ZOOM_OUT]
    # At correct zoom, negative remaining value
    elif remain_val < 0:
        return ACTION2IDX[SUBTRACT_ONE]
    # At correct zoom, positive remaining value
    else:
        return ACTION2IDX[ADD_ONE]
