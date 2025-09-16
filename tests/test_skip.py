import numpy as np
import pytest
from stringart import skip

# ----------------- should_skip_rectangle -----------------
def test_should_skip_rectangle_basic():
    nails = np.array([[0,0], [0,1], [1,0]])
    # same side nails must be skipped
    assert skip.should_skip_rectangle(0, 1, nails)
    # different sides nails must not be skipped
    assert not skip.should_skip_rectangle(1, 2, nails)
    # same nail must be skipped
    assert skip.should_skip_rectangle(0, 0, nails)

def test_should_skip_rectangle_invalid_input():
    nails = np.array([[0,0], [1,1]])
    with pytest.raises(ValueError):
        # indices must be int
        skip.should_skip_rectangle("not an int", 0, nails)
    with pytest.raises(ValueError):
        # indices must be int
        skip.should_skip_rectangle(0, "not an int", nails)
    with pytest.raises(IndexError):
        # no index must exceed len(nails)
        skip.should_skip_rectangle(0, 2, nails)
    with pytest.raises(IndexError):
        # no index must go below 0
        skip.should_skip_rectangle(-1, 1, nails)
    with pytest.raises(ValueError):
        # nail_positions must be an array
        skip.should_skip_rectangle(0, 1, "not an array")
    with pytest.raises(ValueError):
        # nail_positions must be a 2D array
        skip.should_skip_rectangle(0, 1, np.arange(10))

# ----------------- should_skip_circle -----------------
def test_should_skip_circle_basic():
    angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
    # adjacent nails must be skipped for pi/4
    assert skip.should_skip_circle(0, 1, angles, min_angle_diff=np.pi/4)
    # distant nails must not be skipped
    assert not skip.should_skip_circle(0, 2, angles, min_angle_diff=np.pi/4)

def test_should_skip_circle_invalid_input():
    angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
    with pytest.raises(ValueError):
        # indices must be int
        skip.should_skip_circle("not an int", 0, angles, np.pi/8)
    with pytest.raises(ValueError):
        # indices must be int
        skip.should_skip_circle(0, "not an int", angles, np.pi/8)
    with pytest.raises(IndexError):
        # no index must go below 0
        skip.should_skip_circle(-1, 1, angles)
    with pytest.raises(IndexError):
        # no index must exceed len(angles)
        skip.should_skip_circle(0, 10, angles)
    with pytest.raises(ValueError):
        # min_angle_diff cannot negative
        skip.should_skip_circle(0, 1, angles, min_angle_diff=-1)
    with pytest.raises(ValueError):
        # min_angle_diff cannot exceed 2pi (the function uses diff % 2pi)
        skip.should_skip_circle(0, 1, angles, min_angle_diff=10)
    with pytest.raises(ValueError):
        # angles must be an array
        skip.should_skip_circle(0, 0, "not an array")
    with pytest.raises(ValueError):
        # angles must be a 1D array
        skip.should_skip_circle(0, 0, np.arange(10).reshape((2, 5)))

# ----------------- get_should_skip_function -----------------
def test_get_should_skip_function_rectangle():
    nails = np.array([[0, 0], [0, 1], [1, 1]])
    func = skip.get_should_skip_function("rectangle", nails)
    # must return a callable function
    assert callable(func)
    # same nail must be skipped
    assert func(0, 0)
    # same side nails must be skipped
    assert func(0, 1)
    # different side nails must not be skipped
    assert not func(0, 2)

def test_get_should_skip_function_circle():
    angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
    func = skip.get_should_skip_function("circle", angles, min_angle_diff=np.pi/2)
    # must return a callable function
    assert callable(func)
    # too close nails must be skipped
    assert func(0, 1)
    # far away nails must not be skipped
    assert not func(0, 3)

def test_get_should_skip_function_invalid_layout():
    with pytest.raises(ValueError):
        # layout must be circle or rectangle
        skip.get_should_skip_function("triangle")
    with pytest.raises(ValueError):
        # either positions or angles must be passed
        skip.get_should_skip_function("rectangle", None)
    with pytest.raises(ValueError):
        # positions or angles must be an array
        skip.get_should_skip_function("rectangle", "not an array")
    with pytest.raises(ValueError):
        # with layout set to rectangle positions array must be 2D
        skip.get_should_skip_function("rectangle", np.arange(10))
    with pytest.raises(ValueError):
        # either positions or angles must be passed
        skip.get_should_skip_function("circle", None)
    with pytest.raises(ValueError):
        # positions or angles must be an array
        skip.get_should_skip_function("circle", "not an array")
    with pytest.raises(ValueError):
        # with layout set to circle the angles array must be 1D
        skip.get_should_skip_function("circle", np.arange(10).reshape((2, 5)))
    with pytest.raises(ValueError):
        # no index must be less than 0
        skip.get_should_skip_function("circle", np.arange(10), -1)
    with pytest.raises(ValueError):
        # no index must be more than len(array)
        skip.get_should_skip_function("circle", np.arange(10), 10)