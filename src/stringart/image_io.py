import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pathlib import Path
from .pathfinding import get_aa_line_with_cache
from .transforms import rgb2gray, center_square_crop
from .canvas import create_canvas_and_nail_positions

def open_image(img_path: str | Path):
    """Load an image from a file path as a numpy array.

    Parameters
    ----------
    img_path : str or pathlib.Path
        Path to the image file.

    Returns
    -------
    img : array
        Image as a numpy array of shape `(H, W)` for grayscale or `(H, W, C)` for RGB/RGBA.
    """
    p = Path(img_path)
    if not p.exists():
        raise FileNotFoundError(f"Image file not found: {img_path}")
    return np.array(Image.open(img_path))

def replace_transparent_background(img: np.ndarray,
                                   background_color: tuple[int] | list[int] = (50, 50, 50)):
    """Replace the transparent background in a PNG image with a solid color.

    Parameters
    ----------
    img : array
        Input image array with shape `(H, W, 4)`, including an alpha channel.
    background_color : tuple of int or list of int, default (50, 50, 50)
        RGB color to replace transparent regions. Values must be in [0, 255].

    Returns
    -------
    composited_img : array
        Image array with shape `(H, W, 3)`, where the transparent background is replaced by `background_color`.
    """
    if not isinstance(img, np.ndarray):
        raise TypeError("`img` must be a numpy array")
    if img.ndim != 3 or img.shape[2] < 4:
        raise ValueError(f"Provided image must have shape (H, W, 4); got {img.shape} instead")
    if len(background_color) != 3:
        raise ValueError(f"`background_color` must be length 3; got {background_color} instead")
    if np.any(np.array(background_color) < 0) or np.any(np.array(background_color) > 255):
        raise ValueError(f"`background_color` values must be in [0,255]; got {background_color} instead")
    
    # Separate color and alpha channel
    rgb   = img[:, :, :3]
    alpha = img[:, :, 3]

    # Create a background image of the same size
    bg = np.ones_like(rgb, dtype=np.uint8) * np.array(background_color, dtype=np.uint8)

    # Use alpha channel as a mask: blend RGB over new background
    alpha_normalized = alpha[:, :, np.newaxis] / 255.0
    composited = (rgb * alpha_normalized + bg * (1 - alpha_normalized)).astype(np.uint8)

    return composited

def open_grayscale_crop_fixbg_img(img_path: str | Path, background_color: tuple[int] | list[int], nail_layout: str):
    """Open an image, convert it to grayscale, fix transparent background, and crop for circular layouts.

    Parameters
    ----------
    img_path : str or pathlib.Path
        Path to the image file.
    background_color : tuple of int or list of int
        RGB color to replace transparent background if present.
    nail_layout : {"circle", "rectangle"}
        Layout of nails; if "circle", the image is center-cropped to a square.

    Returns
    -------
    img : array
        2D grayscale image array, optionally cropped (if `nail_layout=="circle"`) and with transparent background replaced (if originally present).
    """
    img = open_image(img_path)
    if img.ndim == 3:
        if img.shape[2] == 4:
            img = replace_transparent_background(img, background_color)
        img = rgb2gray(img)
    elif img.ndim == 2:
        pass # already grayscale
    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")

    if nail_layout == 'circle':
        img = center_square_crop(img) # after grayscale
    elif nail_layout != 'rectangle':
        raise ValueError(f"`nail_layout` must be 'circle' or 'rectangle'; got {nail_layout} instead")

    return img

def from_string_idx_order_to_image_array(string_idx_order: np.ndarray, shape: tuple[int],
                                         nail_layout: str, num_nails: int, string_strength: float):
    """Reconstruct a canvas image from a sequence of nail indices.

    Parameters
    ----------
    string_idx_order : array of int
        Sequence of nail indices representing the order in which strings are drawn.
    shape : tuple of int
        Shape of the canvas `(height, width)`.
    nail_layout : {"circle", "rectangle"}
        Layout of nails.
    num_nails : int
        Total number of nails on the canvas.
    string_strength : float
        Strength of the string; controls how much each line darkens the canvas.

    Returns
    -------
    canvas : array
        2D array of floats in [0, 1] representing the reconstructed string art image.
    """
    if len(string_idx_order) < 2:
        raise ValueError("`string_idx_order` must have at least 2 nails")
    if string_strength <= 0:
        raise ValueError("`string_strength` must be positive")
    
    canvas, nail_positions, _ = create_canvas_and_nail_positions(
        shape = shape, nail_layout = nail_layout, num_nails = num_nails
    )
    for from_idx, to_idx in zip(string_idx_order[:-1], string_idx_order[1:]):
        line, rr, cc, _ = get_aa_line_with_cache(from_idx, to_idx, nail_positions, string_strength, canvas)
        canvas[rr, cc] = line
    return canvas

def save_stringart(canvas: np.ndarray, path: str):
    """Save a string art canvas to disk as an image or PDF.

    Parameters
    ----------
    canvas : array
        2D array of floats in [0, 1] representing the canvas.
    path : str
        File path to save the image. Supported extensions: `.png`, `.jpg`, `.pdf`.
    """
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        fig, ax = plt.subplots()
        ax.imshow(canvas, cmap="gray", vmin=0, vmax=1)
        ax.axis("off")
        fig.savefig(path)
        plt.close(fig)
    else:
        plt.imsave(path, canvas, cmap="gray", vmin=0, vmax=1)

def resolve_output_path(user_path: str, default_name: str, allowed_exts: str | list[str] = None):
    """
    Resolves the path where to save a file, allowing multiple extensions.
    
    Parameters
    ----------
    user_path : str
        Path provided by the user. Can be a folder or a file.

    default_name : str
        Default filename to use if user_path is a folder.

    allowed_exts : list[str], optional
        List of allowed file extensions (with leading dot, e.g., ['.png', '.jpg']).
    
    Returns
    -------
    pathlib.Path
        Resolved full path to the file.
    """
    p = Path(user_path)
    
    if not default_name:
        raise ValueError("`default_name` must be a non-empty string")

    # If path is a folder or has no suffix, append default name
    if p.is_dir() or p.suffix == "":
        full_path = p / default_name
    else:
        full_path = p

    # Validate extension
    if allowed_exts:
        if full_path.suffix.lower() not in [ext.lower() for ext in allowed_exts]:
            # If invalid, replace with first allowed extension
            full_path = full_path.with_suffix(allowed_exts[0])

    return full_path