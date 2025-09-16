import numpy as np
from functools import partial

def should_skip_rectangle(from_idx: int, to_idx: int, nail_positions: np.ndarray):
    """Determine whether a pair of nails on a rectangle should be skipped.

    Nails are skipped if they lie on the same side of the rectangle or are the same nail.

    Parameters
    ----------
    from_idx : int
        Index of the first nail in the pair.
    to_idx : int
        Index of the second nail in the pair.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.

    Returns
    -------
    should_skip : bool
        True if the nails are on the same side or identical; False otherwise.
    """
    if not isinstance(from_idx, (np.integer, int)) or not isinstance(to_idx, (np.integer, int)):
        raise ValueError(f"`from_idx` and `to_idx` must be int; got {type(from_idx)} and {type(to_idx)} instead")
    if not isinstance(nail_positions, np.ndarray) or nail_positions.ndim != 2 or nail_positions.shape[1] != 2:
        raise ValueError(f"`nail_positions` must be a 2D numpy array with 2 columns; got {getattr(nail_positions, 'shape', None)} instead")
    if not (0 <= from_idx < len(nail_positions)) or not (0 <= to_idx < len(nail_positions)):
        raise IndexError(f"`from_idx` and `to_idx` must be valid indices (i.e. between {0} and {len(nail_positions)}); got {from_idx}, {to_idx} instead")
    
    return np.any(nail_positions[from_idx] == nail_positions[to_idx])

def should_skip_circle(from_idx: int, to_idx: int, nail_angles: np.ndarray, min_angle_diff: float = np.pi/8):
    """Determine whether a pair of nails on a circle should be skipped due to being too close.

    Parameters
    ----------
    from_idx : int
        Index of the first nail in the pair.
    to_idx : int
        Index of the second nail in the pair.
    nail_angles : array
        Array of shape `(num_nails,)` containing nail angles in radians (0 to 2π, 0 and 2π not repeated).
    min_angle_diff : float, default π/8
        Minimum allowed angular distance between consecutive nails.

    Returns
    -------
    should_skip : bool
        True if the angular distance between the nails is less than `min_angle_diff`; False otherwise.
    """
    if not isinstance(from_idx, (np.integer, int)) or not isinstance(to_idx, (np.integer, int)):
        raise ValueError(f"`from_idx` and `to_idx` must be int; got {type(from_idx)} and {type(to_idx)} instead")
    if not isinstance(nail_angles, np.ndarray) or nail_angles.ndim != 1:
        raise ValueError(f"`nail_angles` must be a 1D numpy array; got {getattr(nail_angles, 'shape', None)} instead")
    if min_angle_diff < 0 or min_angle_diff > 2*np.pi:
        raise ValueError(f"`min_angle_diff` must be in [0, 2*pi]; got {min_angle_diff} instead")
    if not (0 <= from_idx < len(nail_angles)) or not (0 <= to_idx < len(nail_angles)):
        raise IndexError(f"`from_idx` and `to_idx` must be valid indices; got {from_idx}, {to_idx} instead")
    
    diff = np.abs(nail_angles[from_idx] - nail_angles[to_idx]) % (2 * np.pi) # account for periodicity
    diff = min(diff, 2 * np.pi - diff) # get smallest angular distance between two nails on the circle, regardless of direction.
    # going clockwise and counterclockwise we get x and 2*pi-x; min(...) selects the true circular distance between points.
    # e.g. 350 deg - 10 deg = 340 deg, but actually the true distance is 20 deg
    return diff < min_angle_diff

def get_should_skip_function(nail_layout: str, positions_or_angles: np.ndarray = None, min_angle_diff: float = np.pi / 8):
    """Return a function that determines whether a nail pair should be skipped based on layout.

    For rectangle layouts, returns a function that skips nails on the same side.
    For circle layouts, returns a function that skips nails that are too close in angle.

    Parameters
    ----------
    nail_layout : {"circle", "rectangle"}
        Layout of the nails.
    positions_or_angles : array, optional
        For rectangle: `(num_nails, 2)` nail positions.  
        For circle: `(num_nails,)` nail angles in radians.
    min_angle_diff : float, default π/8
        Minimum angular difference for circle layouts. Ignored for rectangle layouts.

    Returns
    -------
    should_skip : callable
        Function `should_skip(i, j)` returning True if the nail pair `(i, j)` should be skipped.
    """
    if nail_layout == 'rectangle':
        if positions_or_angles is None:
            raise ValueError("`positions_or_angles` must be provided for rectangle layout")
        if not isinstance(positions_or_angles, np.ndarray) or positions_or_angles.ndim != 2 or positions_or_angles.shape[1] != 2:
            raise ValueError(f"For rectangle layout `positions_or_angles` must be `positions`, i.e. a 2D numpy array with 2 columns; got {getattr(positions_or_angles, 'shape', None)} instead")
        
        return partial(should_skip_rectangle, nail_positions = positions_or_angles)
    
    elif nail_layout == 'circle':
        if positions_or_angles is None:
            raise ValueError("`positions_or_angles` must be provided for circle layout")
        if not isinstance(positions_or_angles, np.ndarray) or positions_or_angles.ndim != 1:
            raise ValueError(f"For circle layout `positions_or_angles` must be `angles`, i.e. a 1D numpy array; got {getattr(positions_or_angles, 'shape', None)} instead")
        if min_angle_diff < 0 or min_angle_diff > 2*np.pi:
            raise ValueError(f"`min_angle_diff` must be in [0, 2*pi]; got {min_angle_diff} instead")

        if min_angle_diff == 0:
            return lambda i, j: False
        else:
            return partial(should_skip_circle, nail_angles = positions_or_angles, min_angle_diff=min_angle_diff)
    else:
        raise ValueError(f'`nail_layout` must be either "rectangle" or "circle"; got {nail_layout} instead')