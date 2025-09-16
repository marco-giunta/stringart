import numpy as np
from skimage.color import rgb2gray as skimg_rgb2gray
from skimage.transform import rescale as skimg_rescale

def center_square_crop(img: np.ndarray):
    """Crop a 2D image to a centered square.

    If the input image is rectangular, this function crops the largest possible square
    from the center of the image.

    Parameters
    ----------
    img : array
        2D image array of shape `(height, width)`.

    Returns
    -------
    cropped_img : array
        Center-cropped square image of shape `(side, side)`, where `side = min(height, width)`.
    """
    if not isinstance(img, np.ndarray) or img.ndim != 2:
        raise ValueError(f"`img` must be a 2D numpy array, got shape {getattr(img, 'shape', None)}")
    
    height, width = img.shape
    side = min(height, width)
    start_y = (height - side) // 2
    start_x = (width - side) // 2
    return img[start_y:start_y + side, start_x:start_x + side]

def rgb2gray(img: np.ndarray):
    """Convert an RGB image to grayscale.

    Uses `skimage.color.rgb2gray` internally.

    Parameters
    ----------
    img : array
        2D grayscale image or 3D RGB image array of shape `(height, width, 3)`.

    Returns
    -------
    gray_img : array
        2D grayscale image with values in [0, 1].
    """
    if not isinstance(img, np.ndarray):
        raise ValueError(f"`img` must be a numpy array, got {type(img)}")
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError(f"`img` must have shape (H, W, 3), got {img.shape}")
    return skimg_rgb2gray(img)

def downscale(img: np.ndarray, downscale_factor: float):
    """Downscale an image by a specified factor using anti-aliasing.

    Parameters
    ----------
    img : array
        Input image (2D grayscale or 3D RGB).
    downscale_factor : float
        Factor to downscale the image. Must be >0 and <=1.  
        Values <1 shrink the image; values >1 or <=0 are invalid.
        Value 1 does no downscaling.

    Returns
    -------
    downscaled_img : array
        Downscaled image, same number of channels as the input.
    
    Raises
    ------
    ValueError
        If `downscale_factor` is <=0 or >1.
    """
    if not isinstance(downscale_factor, (int, float)):
        raise ValueError(f"`downscale_factor` must be numeric, got {type(downscale_factor)}")
    if downscale_factor > 1 or downscale_factor <= 0:
        raise ValueError(f'`downscale_factor` must be >=0 and <1; got {downscale_factor} instead')
    return skimg_rescale(img, downscale_factor, anti_aliasing = True)