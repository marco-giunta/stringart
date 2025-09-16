import numpy as np
from tqdm import trange
from .pathfinding import get_aa_line_no_cache
from .canvas import create_canvas
from .skip import get_should_skip_function

def precache_lines(nail_positions: np.ndarray, string_strength: float, canvas_shape: tuple[int], should_skip: callable):
    """Precompute and cache anti-aliased line coordinates for all valid nail pairs.

    Parameters
    ----------
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    string_strength : float
        Strength of the string; used to compute pixel intensity values along lines.
    canvas_shape : tuple of int
        Shape of the canvas on which lines will be drawn.
    should_skip : callable
        Function that returns True for nail pairs that should be skipped (e.g., invalid connections).

    Returns
    -------
    line_cache_dict : dict
        Dictionary mapping sorted nail index pairs `(i, j)` to a tuple `(rr, cc, val)`, where `rr` and `cc`
        are pixel coordinates along the line and `val` are anti-aliased intensity values.
    """
    if not isinstance(nail_positions, np.ndarray):
        raise ValueError(f"`nail_positions` must be a numpy array; got {type(nail_positions)} instead")
    if not isinstance(string_strength, (np.floating, float)):
        raise ValueError(f"`string_strength` must be float; got {type(string_strength)} instead")
    if len(canvas_shape) != 2:
        raise ValueError(f"`canvas_shape` must contain exactly 2 positive integers; got {canvas_shape} instead")
    if not isinstance(canvas_shape, (tuple, list)) or not all(isinstance(s, (np.integer, int)) and s > 0 for s in canvas_shape):
        raise ValueError(f"`canvas_shape` must be a tuple or list of positive integers; got {canvas_shape} instead")
    if not callable(should_skip):
        raise ValueError(f"`should_skip` must be callable")

    if nail_positions.ndim != 2 or nail_positions.shape[1] != 2:
        raise ValueError(f"nail_positions must be a `(num_nails, 2)` array; got shape {nail_positions.shape} instead")
    if string_strength <= 0:
        raise ValueError("`string_strength` must be positive")

    empty_canvas = create_canvas(canvas_shape)
    line_cache_dict = {}

    for i in trange(len(nail_positions)):
        for j in range(len(nail_positions)):
            if i == j:
                continue
            if should_skip(i, j):
                continue
            key = tuple(sorted((i, j)))
            if key in line_cache_dict:
                continue
            _, rr, cc, val = get_aa_line_no_cache(i, j, nail_positions, string_strength, empty_canvas)
            line_cache_dict[key] = (rr, cc, val)
    return line_cache_dict

def get_aa_line_from_precache(from_idx: int, to_idx: int, picture: np.ndarray, string_strength: float, line_cache_dict: dict):
    """Retrieve a line from the precomputed cache and draw it on the current picture.

    Parameters
    ----------
    from_idx : int
        Index of the starting nail.
    to_idx : int
        Index of the ending nail.
    picture : array
        2D array representing the current canvas or working image.
    string_strength : float
        Scalar strength of the string; controls how much the line darkens the canvas.
    line_cache_dict : dict
        Precomputed line cache from `precache_lines`.

    Returns
    -------
    line : array or None
        Updated pixel values along the line. None if the line is not in the cache.
    rr : array or None
        Row indices of pixels along the line. None if not cached.
    cc : array or None
        Column indices of pixels along the line. None if not cached.
    val : array or None
        Anti-aliased intensity values for the line. None if not cached.
    """
    if not isinstance(from_idx, (np.integer, int)) or not isinstance(to_idx, (np.integer, int)):
        raise ValueError(f"`from_idx` and `to_idx` must be int; got {type(from_idx)} and {type(to_idx)} instead")
    if not isinstance(picture, np.ndarray):
        raise ValueError(f"`picture` must be a numpy array; got {type(picture)} instead")
    if not isinstance(string_strength, (np.floating, float)):
        raise ValueError(f"`string_strength` must be float; got {type(string_strength)} instead")
    if not isinstance(line_cache_dict, dict):
        raise ValueError(f"`line_cache_dict` must be dict; got {type(line_cache_dict)} instead")

    if not (0 <= from_idx) or not (0 <= to_idx): # cannot infer num_nails trivially from len(cache_dict) due to cache and skip functionality (return None for skipped pairs, etc.)
        raise IndexError(f"`from_idx` and `to_idx` must be valid indices (i.e. >=0); got {from_idx} and {to_idx} instead")
    if picture.ndim != 2:
        raise ValueError(f"picture must be a `(H, W)` array; got shape {picture.shape} instead")
    if np.any(picture < 0) or np.any(picture > 1):
        raise ValueError(f"picture array elements must be in [0, 1] range")
    if string_strength <= 0:
        raise ValueError("`string_strength` must be >0")

    return _get_aa_line_from_precache(
        from_idx=from_idx,
        to_idx=to_idx,
        picture=picture,
        string_strength=string_strength,
        line_cache_dict=line_cache_dict
    )

def _get_aa_line_from_precache(from_idx: int, to_idx: int, picture: np.ndarray, string_strength: float, line_cache_dict: dict):
    """Retrieve a line from the precomputed cache and draw it on the current picture. (No input validation version)

    Parameters
    ----------
    from_idx : int
        Index of the starting nail.
    to_idx : int
        Index of the ending nail.
    picture : array
        2D array representing the current canvas or working image.
    string_strength : float
        Scalar strength of the string; controls how much the line darkens the canvas.
    line_cache_dict : dict
        Precomputed line cache from `precache_lines`.

    Returns
    -------
    line : array or None
        Updated pixel values along the line. None if the line is not in the cache.
    rr : array or None
        Row indices of pixels along the line. None if not cached.
    cc : array or None
        Column indices of pixels along the line. None if not cached.
    val : array or None
        Anti-aliased intensity values for the line. None if not cached.
    """
    key = tuple(sorted((from_idx, to_idx)))
    if key not in line_cache_dict:
        return None, None, None, None
    rr, cc, val = line_cache_dict.get(key)
    line = picture[rr, cc] - string_strength * val
    line = np.clip(line, a_min=0, a_max=1)
    # val can be cached, but not line, as that must be drawn on top of the current state of the canvas
    return line, rr, cc, val

def get_next_nail_position_precache(current_nail_idx: int, canvas: np.ndarray, nail_positions: np.ndarray,
                                    original_img: np.ndarray, string_strength: float, line_cache_dict: dict):
    """Select the next nail that maximally reduces the MSE using precomputed lines.

    Parameters
    ----------
    current_nail_idx : int
        Index of the current nail.
    canvas : array
        2D array representing the current canvas state.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    original_img : array
        2D array representing the target image to approximate.
    string_strength : float
        Strength of the string; controls how much the line darkens the canvas.
    line_cache_dict : dict
        Dictionary of precomputed lines from `precache_lines`.

    Returns
    -------
    best_nail_idx : int or None
        Index of the next nail that gives the best improvement. None if no valid move exists.
    new_canvas : array or None
        Updated canvas after drawing the line. None if no valid move exists.
    distance : float or None
        Mean squared error between the updated canvas and the original image. None if no valid move exists.
    best_improvement : float
        Reduction in squared error achieved by this move.
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
    if not isinstance(line_cache_dict, dict):
        raise ValueError(f"`line_cache_dict` must be dict; got {type(line_cache_dict)} instead")
    
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

    return _get_next_nail_position_precache(
        current_nail_idx=current_nail_idx,
        canvas=canvas,
        nail_positions=nail_positions,
        original_img=original_img,
        string_strength=string_strength,
        line_cache_dict=line_cache_dict
    )

def _get_next_nail_position_precache(current_nail_idx: int, canvas: np.ndarray, nail_positions: np.ndarray,
                                    original_img: np.ndarray, string_strength: float, line_cache_dict: dict):
    """Select the next nail that maximally reduces the MSE using precomputed lines. (No input validation version)

    Parameters
    ----------
    current_nail_idx : int
        Index of the current nail.
    canvas : array
        2D array representing the current canvas state.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    original_img : array
        2D array representing the target image to approximate.
    string_strength : float
        Strength of the string; controls how much the line darkens the canvas.
    line_cache_dict : dict
        Dictionary of precomputed lines from `precache_lines`.

    Returns
    -------
    best_nail_idx : int or None
        Index of the next nail that gives the best improvement. None if no valid move exists.
    new_canvas : array or None
        Updated canvas after drawing the line. None if no valid move exists.
    distance : float or None
        Mean squared error between the updated canvas and the original image. None if no valid move exists.
    best_improvement : float
        Reduction in squared error achieved by this move.
    """

    best_improvement = -1
    best_nail_idx = None
    best_line = None

    for nail_idx in range(len(nail_positions)):
        if nail_idx == current_nail_idx:
            continue # skip same nail

        candidate_line, rr, cc, _ = _get_aa_line_from_precache(current_nail_idx, nail_idx, canvas, string_strength, line_cache_dict)
        if candidate_line is None:
            continue # candidate line not in the cache = flagged by skip function

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

def get_optimal_string_path_precache(canvas: np.ndarray, nail_positions: np.ndarray, original_img: np.ndarray,
                                     string_strength: float, max_num_iter: int,
                                     nail_layout: str, nail_angles: np.ndarray = None, min_angle_diff: float = np.pi / 8,
                                     patience: int = 20, epsilon: float = 1e-6,
                                     line_cache_dict: dict = None):
    """Compute an optimal sequence of nails using precomputed line cache for efficiency.

    Parameters
    ----------
    canvas : array
        Initial canvas (white background) as a 2D array.
    nail_positions : array
        Array of shape `(num_nails, 2)` containing nail positions in `(row, column)` coordinates.
    original_img : array
        2D array representing the target image to approximate.
    string_strength : float
        Scalar strength of the string; controls how much each line darkens the canvas.
    max_num_iter : int
        Maximum number of strings/iterations to perform.
    nail_layout : {"circle", "rectangle"}
        Layout of the nails; affects candidate skipping rules.
    nail_angles : array, optional
        Array of nail angles in radians, required for circular layouts.
    min_angle_diff : float, default np.pi / 8
        Minimum allowed angular difference between consecutive lines (for circular layouts).
    patience : int, default 20
        Number of consecutive iterations with negligible improvement before early stopping.
    epsilon : float, default 1e-6
        Threshold for determining negligible improvement.
    line_cache_dict : dict, default None
        Dictionary of precomputed lines from `precache_lines`; if empty, it will be created using `precache_lines`.
        Use this argument if the cache dict has been computed separately beforehand.

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

    N = max_num_iter + 1
    string_idx_order = np.zeros(N, dtype = int)
    distance_vec = np.zeros(N, dtype = float)

    starting_point_idx = 0
    current_nail_idx = starting_point_idx # maybe add some randomness?
    
    string_idx_order[0] = starting_point_idx
    distance_vec[0] = np.mean((original_img - canvas) ** 2)

    no_improvement_count = 0

    if nail_layout == 'rectangle':
        should_skip = get_should_skip_function('rectangle', nail_positions)
    elif nail_layout == 'circle':
        should_skip = get_should_skip_function('circle', nail_angles, min_angle_diff = min_angle_diff)
    else:
        raise ValueError(f'`nail_layout` must be either "rectangle" or "circle"; got {nail_layout} instead')
    
    if line_cache_dict is None:
        print('Precaching lines...')
        line_cache_dict = precache_lines(nail_positions, string_strength, canvas.shape, should_skip)
        print('Cache done.')
        print('Creating string art...')

    for i in trange(1, N):
        current_nail_idx, new_working_img, current_distance, best_improvement = _get_next_nail_position_precache(
            current_nail_idx, canvas, nail_positions,
            original_img, string_strength, line_cache_dict
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