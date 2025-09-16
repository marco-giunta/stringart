import numpy as np
from skimage.draw import line_aa
from .skip import get_should_skip_function
from tqdm import trange
import functools

def cache_numpy(func: callable):
    """Cache a function with numpy.ndarray arguments."""
    if not callable(func):
        raise ValueError(f"`func` must be callable")
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Convert all numpy arrays in args and kwargs to bytes
        def make_hashable(x):
            if isinstance(x, np.ndarray):
                return x.tobytes()
            return x

        key = tuple(make_hashable(a) for a in args)
        key += tuple((k, make_hashable(v)) for k, v in sorted(kwargs.items()))

        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper

@cache_numpy
def get_aa_line_coordinates_with_cache(from_idx: int, to_idx: int, nail_positions: np.ndarray):
    """Get anti-aliased line pixel coordinates and values. Lines are cached as they are computed.

    Parameters
    ----------
    from_idx : int
        Integer index of starting position nail from `nail_positions`.
    
    to_idx : int
        Integer index of ending position nail from `nail_positions`.
    
    nail_positions : array
        Array of shape `(num_nails, 2)`, containing the nails positions in the (row, column) coordinate system.
    
    Returns
    -------
    rr, cc, val : (N,) ndarray (int, int, float)
        Indices of pixels (`rr`, `cc`) and intensity values (`val`). `img[rr, cc] = val`.

    See also
    --------
    skimage.draw.line_aa : function used to compute the anti-aliased line pixel coordinates/values.
    """
    if not isinstance(from_idx, (np.integer, int)) or not isinstance(to_idx, (np.integer, int)):
        raise ValueError(f"`from_idx` and `to_idx` must be int; got {type(from_idx)} and {type(to_idx)} instead")
    if not isinstance(nail_positions, np.ndarray):
        raise ValueError(f"`nail_positions` must be a numpy array; got {type(nail_positions)} instead")
    
    if not (0 <= from_idx < len(nail_positions)) or not (0 <= to_idx < len(nail_positions)):
        raise IndexError(f"`from_idx` and `to_idx` must be valid indices (i.e. between {0} and {len(nail_positions)}); got {from_idx}, {to_idx} instead")
    if nail_positions.ndim != 2 or nail_positions.shape[1] != 2:
        raise ValueError(f"nail_positions must be a `(num_nails, 2)` array; got shape {nail_positions.shape} instead")
    
    from_pos, to_pos = nail_positions[from_idx], nail_positions[to_idx]
    rr, cc, val = line_aa(from_pos[0], from_pos[1], to_pos[0], to_pos[1])

    return rr, cc, val

@cache_numpy
def _get_aa_line_coordinates_with_cache(from_idx: int, to_idx: int, nail_positions: np.ndarray):
    """Get anti-aliased line pixel coordinates and values. Lines are cached as they are computed. (No input validation version)

    Parameters
    ----------
    from_idx : int
        Integer index of starting position nail from `nail_positions`.
    
    to_idx : int
        Integer index of ending position nail from `nail_positions`.
    
    nail_positions : array
        Array of shape `(num_nails, 2)`, containing the nails positions in the (row, column) coordinate system.
    
    Returns
    -------
    rr, cc, val : (N,) ndarray (int, int, float)
        Indices of pixels (`rr`, `cc`) and intensity values (`val`). `img[rr, cc] = val`.

    See also
    --------
    skimage.draw.line_aa : function used to compute the anti-aliased line pixel coordinates/values.
    """

    from_pos, to_pos = nail_positions[from_idx], nail_positions[to_idx]
    rr, cc, val = line_aa(from_pos[0], from_pos[1], to_pos[0], to_pos[1])

    return rr, cc, val

def get_aa_line_with_cache(from_idx: int, to_idx: int, nail_positions: np.ndarray, string_strength: float, picture: np.ndarray):
    """Get an anti-aliased line from `from_idx` to `to_idx` in `nail_positions` and draw it on the provided picture.

    The line is computed with anti-aliasing using `skimage.draw.line_aa`. The resulting pixel values are subtracted
    from the provided `picture` multiplied by `string_strength` (to darken/thicken the line). Lines are cached for efficiency.

    Parameters
    ----------
    from_idx : int
        Integer index of the starting nail in `nail_positions`.
    to_idx : int
        Integer index of the ending nail in `nail_positions`.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    string_strength : float
        Scalar strength ("thickness") of the string; controls how much the line darkens the canvas (0 = no effect, 1 = fully black).
    picture : array
        2D array of shape `(height, width)` representing the current canvas or working image. Values are in [0, 1].

    Returns
    -------
    line : array
        1D array of same length as the number of pixels along the line; represents the updated pixel values along the line.
    rr : array
        1D array of row indices of the pixels along the line.
    cc : array
        1D array of column indices of the pixels along the line.
    val : array
        1D array of anti-aliased intensity values for each pixel in the line (in [0, 1]).
    """
    if not isinstance(from_idx, (np.integer, int)) or not isinstance(to_idx, (np.integer, int)):
        raise ValueError(f"`from_idx` and `to_idx` must be int; got {type(from_idx)} and {type(to_idx)} instead")
    if not isinstance(nail_positions, np.ndarray):
        raise ValueError(f"`nail_positions` must be a numpy array; got {type(nail_positions)} instead")
    if not isinstance(string_strength, (np.floating, float)):
        raise ValueError(f"`string_strength` must be float; got {type(string_strength)} instead")
    if not isinstance(picture, np.ndarray):
        raise ValueError(f"`picture` must be a numpy array; got {type(picture)} instead")
    
    if not (0 <= from_idx < len(nail_positions)) or not (0 <= to_idx < len(nail_positions)):
        raise IndexError(f"`from_idx` and `to_idx` must be valid indices (i.e. between {0} and {len(nail_positions)}); got {from_idx}, {to_idx} instead")
    if nail_positions.ndim != 2 or nail_positions.shape[1] != 2:
        raise ValueError(f"nail_positions must be a `(num_nails, 2)` array; got shape {nail_positions.shape} instead")
    if string_strength <= 0:
        raise ValueError("`string_strength` must be >0")
    if picture.ndim != 2:
        raise ValueError(f"picture must be a `(H, W)` array; got shape {picture.shape} instead")
    if np.any(picture < 0) or np.any(picture > 1):
        raise ValueError(f"picture array elements must be in [0, 1] range")
    
    return _get_aa_line_with_cache(
        from_idx=from_idx,
        to_idx=to_idx,
        nail_positions=nail_positions,
        string_strength=string_strength,
        picture=picture
    )

def _get_aa_line_with_cache(from_idx: int, to_idx: int, nail_positions: np.ndarray, string_strength: float, picture: np.ndarray):
    """Get an anti-aliased line from `from_idx` to `to_idx` in `nail_positions` and draw it on the provided picture. (No input validation version)

    The line is computed with anti-aliasing using `skimage.draw.line_aa`. The resulting pixel values are subtracted
    from the provided `picture` multiplied by `string_strength` (to darken/thicken the line). Lines are cached for efficiency.

    Parameters
    ----------
    from_idx : int
        Integer index of the starting nail in `nail_positions`.
    to_idx : int
        Integer index of the ending nail in `nail_positions`.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    string_strength : float
        Scalar strength ("thickness") of the string; controls how much the line darkens the canvas (0 = no effect, 1 = fully black).
    picture : array
        2D array of shape `(height, width)` representing the current canvas or working image. Values are in [0, 1].

    Returns
    -------
    line : array
        1D array of same length as the number of pixels along the line; represents the updated pixel values along the line.
    rr : array
        1D array of row indices of the pixels along the line.
    cc : array
        1D array of column indices of the pixels along the line.
    val : array
        1D array of anti-aliased intensity values for each pixel in the line (in [0, 1]).
    """
    
    rr, cc, val = _get_aa_line_coordinates_with_cache(from_idx, to_idx, nail_positions)
    line = picture[rr, cc] - string_strength * val # minus because we're drawing black lines on top of a white canvas
    line = np.clip(line, a_min=0, a_max=1)
    
    return line, rr, cc, val

def get_aa_line_no_cache(from_idx: int, to_idx: int, nail_positions: np.ndarray, string_strength: float, picture: np.ndarray):
    """Get an anti-aliased line from `from_idx` to `to_idx` in `nail_positions` and draw it on `picture` without caching.

    Parameters
    ----------
    from_idx : int
        Integer index of the starting nail in `nail_positions`.
    to_idx : int
        Integer index of the ending nail in `nail_positions`.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    string_strength : float
        Scalar strength of the string; controls how much the line darkens the canvas.
    picture : array
        2D array representing the current canvas or working image. Values are in [0, 1].

    Returns
    -------
    line : array
        1D array of updated pixel values along the line.
    rr : array
        Row indices of the pixels along the line.
    cc : array
        Column indices of the pixels along the line.
    val : array
        Anti-aliased intensity values for each pixel along the line.
    """
    if not isinstance(from_idx, (np.integer, int)) or not isinstance(to_idx, (np.integer, int)):
        raise ValueError(f"`from_idx` and `to_idx` must be int; got {type(from_idx)} and {type(to_idx)} instead")
    if not isinstance(nail_positions, np.ndarray):
        raise ValueError(f"`nail_positions` must be a numpy array; got {type(nail_positions)} instead")
    if not isinstance(string_strength, (np.floating, float)):
        raise ValueError(f"`string_strength` must be float; got {type(string_strength)} instead")
    if not isinstance(picture, np.ndarray):
        raise ValueError(f"`nail_positions` must be a numpy array; got {type(picture)} instead")
    
    if not (0 <= from_idx < len(nail_positions)) or not (0 <= to_idx < len(nail_positions)):
        raise IndexError(f"`from_idx` and `to_idx` must be valid indices (i.e. between {0} and {len(nail_positions)}); got {from_idx}, {to_idx} instead")
    if nail_positions.ndim != 2 or nail_positions.shape[1] != 2:
        raise ValueError(f"nail_positions must be a `(num_nails, 2)` array; got shape {nail_positions.shape} instead")
    if string_strength <= 0:
        raise ValueError("`string_strength` must be positive")
    if picture.ndim != 2:
        raise ValueError(f"picture must be a `(H, W)` array; got shape {nail_positions.shape} instead")
    if np.any(picture < 0) or np.any(picture > 1):
        raise ValueError(f"picture array elements must be in [0, 1] range")
    
    return _get_aa_line_no_cache(
        from_idx=from_idx,
        to_idx=to_idx,
        nail_positions=nail_positions,
        string_strength=string_strength,
        picture=picture
    )

def _get_aa_line_no_cache(from_idx: int, to_idx: int, nail_positions: np.ndarray, string_strength: float, picture: np.ndarray):
    """Get an anti-aliased line from `from_idx` to `to_idx` in `nail_positions` and draw it on `picture` without caching. (No input validation version)

    Parameters
    ----------
    from_idx : int
        Integer index of the starting nail in `nail_positions`.
    to_idx : int
        Integer index of the ending nail in `nail_positions`.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    string_strength : float
        Scalar strength of the string; controls how much the line darkens the canvas.
    picture : array
        2D array representing the current canvas or working image. Values are in [0, 1].

    Returns
    -------
    line : array
        1D array of updated pixel values along the line.
    rr : array
        Row indices of the pixels along the line.
    cc : array
        Column indices of the pixels along the line.
    val : array
        Anti-aliased intensity values for each pixel along the line.
    """

    from_pos, to_pos = nail_positions[from_idx], nail_positions[to_idx]
    rr, cc, val = line_aa(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    line = picture[rr, cc] - string_strength * val 
    line = np.clip(line, a_min=0, a_max=1)

    return line, rr, cc, val

def get_next_nail_position(current_nail_idx: int, canvas: np.ndarray, nail_positions: np.ndarray, original_img: np.ndarray, string_strength: float,
                           should_skip_function : callable,
                           cache_lines: bool = True):
    """Find the next nail that best improves the string art approximation.

    Evaluates all possible candidate nails (skipping invalid ones based on layout rules) and selects the nail
    that maximizes the reduction in L2 error between the current canvas and the target `original_img`.

    Parameters
    ----------
    current_nail_idx : int
        Index of the current nail.
    canvas : array
        2D array representing the current canvas state.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    original_img : array
        2D array of the target image to approximate.
    string_strength : float
        Scalar strength of the string; determines how much the line darkens the canvas.
    should_skip_function : callable
        Function used to determine whether to skip a pair of nails.
    cache_lines : bool, default True
        Whether to cache computed lines for performance.

    Returns
    -------
    best_nail_idx : int or None
        Index of the next nail that gives the best improvement. None if no valid move exists.
    new_canvas : array or None
        Updated canvas after drawing the line to `best_nail_idx`. None if no valid move exists.
    distance : float or None
        Mean squared error between the updated canvas and the original image. None if no valid move exists.
    best_improvement : float
        Improvement in squared error achieved by this move.
    """
    if not isinstance(current_nail_idx, (np.integer, int)):
        raise ValueError(f"`current_nail_idx` must be int; got {type(current_nail_idx)} instead")
    if not isinstance(canvas, np.ndarray):
        raise ValueError(f"`canvas` must be a numpy array; got {type(canvas)} instead")
    if not isinstance(nail_positions, np.ndarray):
        raise ValueError(f"`nail_positions` must be a numpy array; got {type(nail_positions)} instead")
    if not isinstance(original_img, np.ndarray):
        raise ValueError(f"`original_img` must be a numpy array; got {type(original_img)} instead")
    if not isinstance(string_strength, (np.floating, float)):
        raise ValueError(f"`string_strength` must be float; got {type(string_strength)} instead")
    if not isinstance(cache_lines, bool):
        raise ValueError(f"`cache_lines` must be bool; got {type(cache_lines)} instead")
    if not callable(should_skip_function):
        raise ValueError(f"`should_skip_function` must be callable; got {type(should_skip_function)} instead")

    if not (0 <= current_nail_idx <= len(nail_positions)):
        raise IndexError(f"`current_nail_idx` must be a valid index (i.e. between {0} and {len(nail_positions)}; got {current_nail_idx} instead)")
    if canvas.ndim != 2:
        raise ValueError(f"picture must be a `(H, W)` array; got shape {nail_positions.shape} instead")
    if np.any(canvas < 0) or np.any(canvas > 1):
        raise ValueError(f"canvas array elements must be in [0, 1] range")
    if nail_positions.ndim != 2 or nail_positions.shape[1] != 2:
        raise ValueError(f"`nail_positions` must be a `(num_nails, 2)` array; got shape {nail_positions.shape} instead")
    if original_img.ndim != 2:
        raise ValueError(f"original_img must be a `(H, W)` array; got shape {nail_positions.shape} instead")
    if np.any(original_img < 0) or np.any(original_img > 1):
        raise ValueError(f"original_img array elements must be in [0, 1] range")
    if string_strength <= 0:
        raise ValueError("`string_strength` must be positive")

    return _get_next_nail_position(
        current_nail_idx=current_nail_idx,
        canvas=canvas,
        nail_positions=nail_positions,
        original_img=original_img,
        string_strength=string_strength,
        should_skip_function=should_skip_function,
        cache_lines=cache_lines
    )

def _get_next_nail_position(current_nail_idx: int, canvas: np.ndarray, nail_positions: np.ndarray, original_img: np.ndarray, string_strength: float,
                           should_skip_function : callable,
                           cache_lines: bool = True):
    """Find the next nail that best improves the string art approximation. (No input validation version)

    Evaluates all possible candidate nails (skipping invalid ones based on layout rules) and selects the nail
    that maximizes the reduction in L2 error between the current canvas and the target `original_img`.

    Parameters
    ----------
    current_nail_idx : int
        Index of the current nail.
    canvas : array
        2D array representing the current canvas state.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    original_img : array
        2D array of the target image to approximate.
    string_strength : float
        Scalar strength of the string; determines how much the line darkens the canvas.
    should_skip_function : callable
        Function used to determine whether to skip a pair of nails.
    cache_lines : bool, default True
        Whether to cache computed lines for performance.

    Returns
    -------
    best_nail_idx : int or None
        Index of the next nail that gives the best improvement. None if no valid move exists.
    new_canvas : array or None
        Updated canvas after drawing the line to `best_nail_idx`. None if no valid move exists.
    distance : float or None
        Mean squared error between the updated canvas and the original image. None if no valid move exists.
    best_improvement : float
        Improvement in squared error achieved by this move.
    """

    best_improvement = -1
    best_nail_idx = None
    best_line = None

    get_aa_line_fun = _get_aa_line_with_cache if cache_lines else _get_aa_line_no_cache

    for nail_idx in range(len(nail_positions)):
        if nail_idx == current_nail_idx:
            continue # skip same nail
        if should_skip_function(nail_idx, current_nail_idx):
            continue
        
        candidate_line, rr, cc, _ = get_aa_line_fun(current_nail_idx, nail_idx, nail_positions, string_strength, canvas)

        current_error_on_candidate_line = np.sum((canvas[rr, cc] - original_img[rr, cc]) ** 2)
        new_error_on_candidate_line = np.sum((candidate_line - original_img[rr, cc]) ** 2) 
        # we are computing the differences of the L2 norms, meaning that unchanged pixel don't contribute to the current error (square difference components are summed linearly).
        # therefore we ignore them by only evaluating the line differences on the pixels that were actually modified, thus improving performance and ensuring that that difference is correctly equal to 0.

        improvement = current_error_on_candidate_line - new_error_on_candidate_line

        if improvement > best_improvement:
            best_improvement = improvement
            best_nail_idx = nail_idx
            best_line = candidate_line
            best_rr, best_cc = rr, cc

    if best_line is not None:
        new_canvas = canvas
        new_canvas[best_rr, best_cc] = best_line
        distance = np.mean((original_img - new_canvas) ** 2) # normalize wrt image size, otherwise sum
    else:
        new_canvas, distance = None, None

    return best_nail_idx, new_canvas, distance, best_improvement

def get_optimal_string_path(canvas: np.ndarray, nail_positions: np.ndarray, original_img: np.ndarray, string_strength: float, max_num_iter: int,
                            nail_layout: str, nail_angles: np.ndarray = None, min_angle_diff: float = np.pi / 8,
                            cache_lines: bool = True,
                            patience: int = 20, epsilon: float = 1e-6):
    """Compute an optimal sequence of nails to approximate an image with string art.

    Iteratively selects the next nail to draw a string to, updating the canvas and tracking the MSE.
    Stops early if no improvement is seen for `patience` consecutive iterations.

    Parameters
    ----------
    canvas : array
        Initial canvas (white background) as a 2D array.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    original_img : array
        2D array representing the target image to approximate.
    string_strength : float
        Scalar strength of the string; determines how much the line darkens the canvas.
    max_num_iter : int
        Maximum number of strings/iterations to perform.
    nail_layout : {"circle", "rectangle"}
        Layout of the nails; affects candidate skipping rules.
    nail_angles : array, optional
        Array of nail angles in radians, required for circular layouts.
    min_angle_diff : float, default np.pi / 8
        Minimum allowed angular difference between consecutive lines (for circular layouts).
    cache_lines : bool, default True
        Whether to cache computed lines for performance.
    patience : int, default 20
        Number of consecutive iterations with negligible improvement before early stopping.
    epsilon : float, default 1e-6
        Threshold for determining negligible improvement.

    Returns
    -------
    string_idx_order : array
        Array of indices of nails in the order they were selected.
    canvas : array
        Final canvas after all iterations.
    distance_vec : array
        Array of mean squared errors between the canvas and the original image after each iteration.
    """
    if not isinstance(canvas, np.ndarray):
        raise ValueError(f"`canvas` must be a numpy array; got {type(canvas)} instead")
    if not isinstance(nail_positions, np.ndarray):
        raise ValueError(f"`nail_positions` must be a numpy array; got {type(nail_positions)} instead")
    if not isinstance(original_img, np.ndarray):
        raise ValueError(f"`original_img` must be a numpy array; got {type(original_img)} instead")
    if not isinstance(string_strength, (np.floating, float)):
        raise ValueError(f"`string_strength` must be float; got {type(string_strength)} instead")
    if not isinstance(max_num_iter, (np.integer, int)):
        raise ValueError(f"`max_num_iter` must be an int; got {type(max_num_iter)} instead")
    if nail_layout not in ['circle', 'rectangle']:
        raise ValueError(f"`nail_layout` must be either 'circle' or 'rectangle'; got {nail_layout} instead")
    if nail_layout == 'circle':
        if nail_angles is None:
            raise ValueError(f"`nail_angles` cannot be None if `nail_layout=='circle'`")
        if not isinstance(nail_angles, np.ndarray):
            raise ValueError(f"`nail_angles` must be a numpy array; got {type(nail_angles)} instead")
        if min_angle_diff is None:
            raise ValueError(f"`min_angle_diff` cannot be None if `nail_layout=='circle'`")
        if not isinstance(min_angle_diff, (np.floating, float)):
            raise ValueError(f"`min_angle_diff` must be float; got {type(min_angle_diff)} instead")
    if not isinstance(cache_lines, bool):
        raise ValueError(f"`cache_lines` must be bool; got {type(cache_lines)} instead")
    if not isinstance(patience, (np.integer, int)):
        raise ValueError(f"`patience` must be an int; got {type(patience)} instead")
    if not isinstance(epsilon, (np.floating, float)):
        raise ValueError(f"`epsilon` must be float; got {type(epsilon)} instead")

    if canvas.ndim != 2:
        raise ValueError(f"picture must be a `(H, W)` array; got shape {nail_positions.shape} instead")
    if np.any(canvas < 0) or np.any(canvas > 1):
        raise ValueError(f"canvas array elements must be in [0, 1] range")
    if nail_positions.ndim != 2 or nail_positions.shape[1] != 2:
        raise ValueError(f"`nail_positions` must be a `(num_nails, 2)` array; got shape {nail_positions.shape} instead")
    if original_img.ndim != 2:
        raise ValueError(f"original_img must be a `(H, W)` array; got shape {nail_positions.shape} instead")
    if np.any(original_img < 0) or np.any(original_img > 1):
        raise ValueError(f"original_img array elements must be in [0, 1] range")
    if string_strength <= 0:
        raise ValueError("`string_strength` must be positive")
    if max_num_iter <= 0:
        raise ValueError(f"`max_num_iter` must be >=0; got {max_num_iter} instead")
    if nail_angles is not None:
        if nail_angles.ndim != 1:
            raise ValueError(f"`nail_angles` must be a (num_nails, ) array; got shape {nail_angles.shape} instead")
        if len(nail_angles) != len(nail_positions):
            raise ValueError(f"`nail_angles` and `nail_positions` must have matching lengths; got {len(nail_angles)} and {len(nail_positions)} instead")
    if min_angle_diff < 0 or min_angle_diff > 2*np.pi:
        raise ValueError(f"`min_angle_diff` must be in [0, 2*pi]; got {min_angle_diff} instead")
    if patience < 0:
        raise ValueError(f"`patience` must be >=0; got {patience} instead")
    if epsilon <= 0:
        raise ValueError(f"`epsilon` must be >0; got {epsilon} instead")

    if nail_layout == 'rectangle':
        should_skip_function = get_should_skip_function('rectangle', nail_positions)
    elif nail_layout == 'circle':
        should_skip_function = get_should_skip_function('circle', nail_angles, min_angle_diff = min_angle_diff)
    else:
        raise ValueError(f'`nail_layout` must be either "rectangle" or "circle"; got {nail_layout} instead')

    N = max_num_iter + 1
    string_idx_order = np.zeros(N, dtype = int)
    distance_vec = np.zeros(N, dtype = float)

    starting_point_idx = 0
    current_nail_idx = starting_point_idx # maybe add some randomness?
    
    string_idx_order[0] = starting_point_idx
    distance_vec[0] = np.mean((original_img - canvas) ** 2)
    
    no_improvement_count = 0

    for i in trange(1, N):
        current_nail_idx, new_working_img, current_distance, best_improvement = _get_next_nail_position(
            current_nail_idx, canvas, nail_positions,
            original_img, string_strength,
            should_skip_function,
            cache_lines
        )
        if new_working_img is None: 
            break 

        if best_improvement < epsilon:
            no_improvement_count += 1
        else:
            no_improvement_count = 0

        if no_improvement_count >= patience:
            print(f"Stopping early after {i} iterations (patience reached).")
            break

        canvas = new_working_img
        string_idx_order[i] = current_nail_idx
        distance_vec[i] = current_distance

    return string_idx_order, canvas, distance_vec