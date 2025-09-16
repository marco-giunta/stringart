import numpy as np
from .image_io import open_grayscale_crop_fixbg_img
from .transforms import downscale
from .canvas import create_canvas_and_nail_positions
from .pathfinding import get_optimal_string_path
from .pathfinding_precache import get_optimal_string_path_precache
from pathlib import Path

def create_stringart(img_path: str | Path,
                     num_nails: int,
                     downscale_factor: float,
                     string_strength: float = 0.1,
                     max_num_iter: int = 5000,
                     nail_layout: str = 'circle',
                     cache_lines: bool = True,
                     precache_lines: bool = True,
                     min_angle_diff = np.pi / 8,
                     background_color: tuple[int] | list[int] = (50, 50, 50),
                     patience: int = 20,
                     epsilon: float = 1e-6):
    """Generate string art from an input image by computing the optimal nail sequence.

    The function converts the input image to grayscale, optionally downsamples it for faster computation,
    creates a virtual canvas with nails in a circle or rectangle layout, and iteratively selects the sequence
    of nails that best approximates the image with dark string lines. 
    Lines can be cached/precached to speed up the computation.
    The loop stops if no improvement greater than `epsilon` is observed for `patience` consecutive iterations.

    Parameters
    ----------
    img_path : str or path
        Path to the input image. Transparent backgrounds are replaced with `background_color`.
    num_nails : int
        Number of nails to place around the edge of the canvas.
    downscale_factor : float
        Factor to downscale the input image for faster computation.
    string_strength : float, default 0.1
        Intensity of each string line; controls how much it darkens the canvas (0 = no effect, 1 = fully black).
    max_num_iter : int, default 5000
        Maximum number of strings/iterations to draw.
    nail_layout : {"circle", "rectangle"}, default "circle"
        Layout of nails on the canvas.
    cache_lines : bool, default True
        Whether to cache line computations for efficiency.
    precache_lines : bool, default True
        Whether to precache all possible lines before starting if `cache_lines` is True.
    min_angle_diff : float, default π/8
        Minimum allowed angular difference between consecutive lines for circular layouts.
    background_color : tuple of int, default (50, 50, 50)
        RGB color used to replace transparent backgrounds in input images.
    patience : int, default 20
        Number of consecutive iterations with negligible improvement before early stopping.
    epsilon : float, default 1e-6
        Threshold for determining negligible improvement in mean squared error.

    Returns
    -------
    string_idx_order : array of int
        Sequence of nail indices selected to approximate the image.
    canvas : array of float
        Final 2D canvas with string art drawn. Values are in [0, 1].
    distance_vec : array of float
        Array of mean squared errors between the canvas and the original image after each iteration.
    """
    if not isinstance(img_path, (str, Path)):
        raise ValueError(f"`img_path` must be str or pathlib.Path; got {type(img_path)} instead")
    if not isinstance(num_nails, int) or num_nails < 10:
        raise ValueError(f"`num_nails` must be int >= 10; got {num_nails} instead")
    if not isinstance(downscale_factor, (float, int)) or not (0 < downscale_factor <= 1):
        raise ValueError(f"`downscale_factor` must be float in (0, 1]; got {downscale_factor} instead")
    if not isinstance(string_strength, (int, float)) or string_strength <= 0:
        raise ValueError(f"`string_strength` must be positive number; got {string_strength} instead")
    if nail_layout not in {"circle", "rectangle"}:
        raise ValueError(f"`nail_layout` must be 'circle' or 'rectangle'; got {nail_layout} instead")
    if not isinstance(background_color, (tuple, list)) or len(background_color) != 3:
        raise ValueError("`background_color` must be a tuple/list of 3 integers")
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in background_color):
        raise ValueError(f"`background_color` must contain ints in [0, 255]; got {background_color} instead")

    img = open_grayscale_crop_fixbg_img(img_path, background_color, nail_layout)
    img = downscale(img, downscale_factor)

    canvas, nail_positions, nail_angles = create_canvas_and_nail_positions(
        shape = img.shape, nail_layout = nail_layout, num_nails = num_nails
    )

    if cache_lines and precache_lines:
        string_idx_order, canvas, distance_vec = get_optimal_string_path_precache(
            canvas = canvas, 
            nail_positions = nail_positions, 
            original_img = img,
            string_strength = string_strength, 
            max_num_iter = max_num_iter,
            nail_layout = nail_layout,
            nail_angles = nail_angles,
            min_angle_diff = min_angle_diff,
            patience = patience,
            epsilon = epsilon
        )
    else:
        string_idx_order, canvas, distance_vec = get_optimal_string_path(
            canvas = canvas, 
            nail_positions = nail_positions, 
            original_img = img,
            string_strength = string_strength, 
            max_num_iter = max_num_iter,
            nail_layout = nail_layout,
            nail_angles = nail_angles,
            min_angle_diff = min_angle_diff,
            cache_lines = cache_lines,
            patience = patience,
            epsilon = epsilon
        )

    return string_idx_order, canvas, distance_vec