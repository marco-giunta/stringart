import numpy as np

def create_canvas(shape: tuple[int] | list[int]):
    """Create an empty white canvas. 
    The empty canvas is returned as a numpy array of ones with the provided shape.
    
    Parameters
    ----------
    shape : tuple of int or list of int
        Shape of the empty white canvas (array of ones) to be returned.
    
    Returns
    -------
    canvas : array
        Array of ones of provided `shape`.
    """
    if len(shape) != 2:
        raise ValueError(f"`shape` must contain exactly 2 positive integers; got {shape} instead")
    if not isinstance(shape, (tuple, list)) or not all(isinstance(s, (np.integer, int)) and s > 0 for s in shape):
        raise ValueError(f"`shape` must be a tuple or list of positive integers; got {shape} instead")
    return np.ones(shape)

def create_rectangle_nail_positions(shape: tuple[int] | list[int], num_nails: int):
    """Create an array containing the positions of nails placed along a rectangle on the edge of the given canvas.
    
    Parameters
    ----------
    shape : tuple of int or list of int
        Shape of the canvas array around which to place nails.

    num_nails : int
        Number of nails to place around the edge of the canvas,
        linearly spaced around a rectangle.

    Returns
    -------
    nail_positions : array
        Array of shape `(num_nails, 2)`, containing the `num_nails` nail positions in the (row, column) coordinate system.
        Each side of the rectangle contains a fraction of `num_nails`
        proportional to the length of that side compared to the perimeter.
    """
    if num_nails <= 0:
        raise ValueError(f"`num_nails` must be positive; got {num_nails} instead")
    if len(shape) != 2:
        raise ValueError(f"`shape` must contain exactly 2 positive integers; got {shape} instead")
    height, width = shape
    if height <= 0 or width <= 0:
        raise ValueError(f"Canvas dimensions must be positive; got {shape} instead")
    perimeter = 2 * (height + width)

    top_num = int(num_nails * width / perimeter)
    side_num = int(num_nails * height / perimeter)

    top_nails_coords = np.column_stack([
        np.zeros(top_num),
        np.arange(top_num) * width / top_num
    ]).astype(int) # [int(i * width / top_num) for i in range(top_num)]
    
    right_nails_coords = np.column_stack([
        np.arange(side_num) * height / side_num,
        np.full(side_num, width - 1)
    ]).astype(int)

    bottom_nails_coords = np.column_stack([
        np.full(top_num, height - 1),
        width - 1 - np.arange(top_num) * width / top_num
    ]).astype(int)
    
    left_nails_coords = np.column_stack([
        height -1 - np.arange(side_num) * height / side_num,
        np.zeros(side_num)
    ]).astype(int)

    return np.vstack([
        top_nails_coords, right_nails_coords,
        bottom_nails_coords, left_nails_coords
    ])

def create_circle_nail_positions(shape: tuple[int] | list[int], num_nails: int):
    """Create an array containing the positions of nails placed along a circle on the edge of the given canvas.

    Parameters
    ----------
    shape : tuple of int or list of int
        Shape of the canvas array around which to place nails.

    num_nails : int
        Number of nails to place around the edge of the canvas,
        linearly spaced around a circle.
    
    Returns
    -------
    nail_positions : array
        Array of shape `(num_nails, 2)`, containing the `num_nails` nail positions in the (row, column) coordinate system.
    
    nail_angles : array
        Array of shape `(num_nails, )` of `num_nails` linearly spaced nail angles between 0 and 2π
        (0 and 2π are not counted twice).

    """
    if num_nails <= 0:
        raise ValueError(f"`num_nails` must be positive; got {num_nails} instead")
    if len(shape) != 2:
        raise ValueError(f"`shape` must contain exactly 2 positive integers; got {shape} instead")
    height, width = shape
    if height <= 0 or width <= 0:
        raise ValueError(f"Canvas dimensions must be positive; got {shape} instead")
    center_y, center_x = height // 2, width // 2 # assume center crop
    radius = min(center_x, center_y) - 1 # -1 buffer to avoid exiting from canvas due to int approx
    angles = np.linspace(0, 2 * np.pi, num_nails, endpoint=False) # don't count 0=2π twice
    
    rr = center_y - (radius * np.sin(angles)).astype(int) # r/c coordinate system
    cc = center_x + (radius * np.cos(angles)).astype(int)
    return np.column_stack((rr, cc)), angles

def create_canvas_and_nail_positions(shape: tuple[int] | list[int], nail_layout: str, num_nails: int):
    """Create an empty white canvas of provided shape and nails positions array of provided number and geometry.

    Parameters
    ----------
    shape : tuple of int or list of int
        Shape of the canvas around which to place nails.

    nail_layout : {"circle", "rectangle"}
        Geometric layout of the nails; must be either "circle" or "rectangle".

    num_nails : int
        Number of nails to place around the edge of the canvas,
        linearly spaced around a rectangle or a circle.
    
    Returns
    -------
    canvas : array
        Array of ones of provided `shape`.

    nail_positions : array
        Array of shape `(num_nails, 2)`, containing the `num_nails` nail positions in the (row, column) coordinate system.
    
    nail_angles : array
        Array of shape `(num_nails, )` of `num_nails` linearly spaced nail angles between 0 and 2π
        (0 and 2π are not counted twice). This is None if `nail_layout=="rectangle"`.
    """
    if len(shape) != 2:
        raise ValueError(f"`shape` must contain exactly 2 positive integers; got {shape} instead")
    if np.any(np.array(shape) <= 0):
        raise ValueError(f"Canvas dimensions must be positive; got {shape} instead")
    if nail_layout not in ["circle", "rectangle"]:
        raise ValueError(f"`nail_layout` must be 'circle' or 'rectangle'; got {nail_layout} instead")
    if num_nails <= 0:
        raise ValueError(f"`num_nails` must be positive; got {num_nails} instead")
    
    
    canvas = create_canvas(shape)
    if nail_layout == 'circle':
        nail_positions, nail_angles = create_circle_nail_positions(shape, num_nails)
    elif nail_layout == 'rectangle':
        nail_positions = create_rectangle_nail_positions(shape, num_nails)
        nail_angles = None
    else:
        raise ValueError(f'`nail_layout` must be "circle" or "rectangle"; got {nail_layout} instead')

    return canvas, nail_positions, nail_angles