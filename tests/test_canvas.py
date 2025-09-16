import numpy as np
import pytest
from stringart import canvas

# ----------------- create_canvas -----------------
def test_create_canvas_basic():
    shape = (5, 7)
    c = canvas.create_canvas(shape)
    # check result is an array of ones with expected shape
    assert isinstance(c, np.ndarray)
    assert c.shape == shape
    assert np.all(c == 1)

def test_create_canvas_invalid_shape():
    # shape must contain positive numbers
    with pytest.raises(ValueError):
        canvas.create_canvas((-5, 5))
    # shape must contain 2 positive numbers
    with pytest.raises(ValueError):
        canvas.create_canvas((1, 1, 1))
    # shape must be a tuple of int
    with pytest.raises(ValueError):
        canvas.create_canvas("not a tuple of int")
    # shape must be a tuple or list of int
    with pytest.raises(ValueError):
        canvas.create_canvas([5, "a"])

# ----------------- create_rectangle_nail_positions -----------------
def test_create_rectangle_nail_positions_basic():
    shape = (10, 20)
    num_nails = 12
    nails = canvas.create_rectangle_nail_positions(shape, num_nails)
    # check result is an array with expected shape
    assert isinstance(nails, np.ndarray)
    assert nails.shape[0] == 12
    assert nails.shape[1] == 2

def test_create_rectangle_nail_positions_invalid_input():
    # num_nails must be >0
    with pytest.raises(ValueError):
        canvas.create_rectangle_nail_positions((10, 10), 0)
    # shape must be 2D
    with pytest.raises(ValueError):
        canvas.create_rectangle_nail_positions((10, 10, 10), 20)
    # shape must contain 2 positive int
    with pytest.raises(ValueError):
        canvas.create_rectangle_nail_positions((0, 10), 5)

# ----------------- create_circle_nail_positions -----------------
def test_create_circle_nail_positions_basic():
    shape = (10, 10)
    num_nails = 8
    nails, angles = canvas.create_circle_nail_positions(shape, num_nails)
    # check result is an array with expected shape for both positions and angles
    assert isinstance(nails, np.ndarray)
    assert nails.shape == (8, 2)
    assert isinstance(angles, np.ndarray)
    assert angles.shape == (8,)

def test_create_circle_nail_positions_invalid_input():
    # num_nails must be >0
    with pytest.raises(ValueError):
        canvas.create_circle_nail_positions((10, 10), 0)
    # shape must be 2D
    with pytest.raises(ValueError):
        canvas.create_circle_nail_positions((10, 10, 10), 10)
    # shape must contain 2 positive int
    with pytest.raises(ValueError):
        canvas.create_circle_nail_positions((0, 10), 5)

# ----------------- canvas_and_nail_positions -----------------
def test_create_canvas_and_nail_positions_rectangle_basic():
    canvas_array, nails, angles = canvas.create_canvas_and_nail_positions((10, 20), "rectangle", 12)
    # check canvas result is an array with expected shape
    assert canvas_array.shape == (10, 20)
    # layout set to rectangle -> positions must be a 2D array, angles None
    assert nails.shape[0] == 12
    assert nails.shape[1] == 2
    assert angles is None

def test_create_canvas_and_nail_positions_circle_basic():
    canvas_array, nails, angles = canvas.create_canvas_and_nail_positions((10, 20), "circle", 12)
    # check canvas result is an array with expected shape
    assert canvas_array.shape == (10, 20)
    # layout set to circle -> positions must be None, angles a 1D array
    assert nails.shape == (12, 2)
    assert angles.shape == (12, )

def test_create_canvas_and_nail_positions_invalid_input():
    # shape must contain positive ints
    with pytest.raises(ValueError):
        canvas.create_canvas_and_nail_positions((0, 10), "circle", 10)
    # shape must contain exactly 2 numbers
    with pytest.raises(ValueError):
        canvas.create_canvas_and_nail_positions((10, 10, 10), "circle", 10)
    # layout must be "circle" or "rectangle" only
    with pytest.raises(ValueError):
        canvas.create_canvas_and_nail_positions((10, 10), "not circle or rectangle", 10)
    # num_nails must be >0
    with pytest.raises(ValueError):
        canvas.create_canvas_and_nail_positions((10, 10), "circle", 0)