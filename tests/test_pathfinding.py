import numpy as np
import pytest
from stringart import pathfinding

# ---------------- cache_numpy ----------------
def test_cache_numpy_invalid_args():
    with pytest.raises(ValueError):
        # func must be callable
        pathfinding.cache_numpy("not a callable")

# ---------------- get_aa_line_coordinates_with_cache ----------------
def test_get_aa_line_coordinates_with_cache_invalid_args():
    # indices must be int
    nails = np.arange(10).reshape((5, 2))
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_coordinates_with_cache("not an int", 0, nails)
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_coordinates_with_cache(0, "not an int", nails)
    # nail positions must be an array
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_coordinates_with_cache(0, 1, "not an array")
    # indices must be in valid range
    with pytest.raises(IndexError):
        pathfinding.get_aa_line_coordinates_with_cache(-1, 1, nails)
    with pytest.raises(IndexError):
        pathfinding.get_aa_line_coordinates_with_cache(0, 100, nails)
    # nail positions must be a (N, 2) array
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_coordinates_with_cache(0, 1, np.arange(10))
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_coordinates_with_cache(0, 1, np.zeros((10, 3)))

# ---------------- get_aa_line_coordinates_with/no_cache ----------------
def test_get_aa_line_with_cache_and_no_cache_consistency():
    # Minimal setup
    nail_positions = np.array([[0, 0], [0, 5]])
    canvas = np.ones((10, 10), dtype=float)
    string_strength = 0.5

    line1, rr1, cc1, val1 = pathfinding.get_aa_line_with_cache(0, 1, nail_positions, string_strength, canvas)
    line2, rr2, cc2, val2 = pathfinding.get_aa_line_no_cache(0, 1, nail_positions, string_strength, canvas)

    # Coordinates and values should match
    assert np.array_equal(rr1, rr2)
    assert np.array_equal(cc1, cc2)
    assert np.allclose(val1, val2)
    assert np.allclose(line1, line2)
    # Line values should be clipped into [0, 1]
    assert np.all(0 <= line1) and np.all(line1 <= 1)

# ---------------- get_aa_line_with_cache ----------------
def test_get_aa_line_with_cache_invalid_args():
    nail_positions = np.array([[0, 0], [1, 1]])
    canvas = np.ones((5, 5))
    # from_idx must be an int
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache("not an int", 0, nail_positions, 0.1, canvas)
    # to_idx must be an int
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, "not an int", nail_positions, 0.1, canvas)
    # positions must be an array
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 1, "not an array", 0.1, canvas)
    # string_strength must be a float
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 1, nail_positions, "not a float", canvas)
    # canvas must be an array
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 1, nail_positions, 0.1, "not an array")
    # idx must not be out of range
    with pytest.raises(IndexError):
        pathfinding.get_aa_line_with_cache(0, 5, nail_positions, 0.1, canvas)
    # nail_positions must have ndim==2
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 0, np.arange(10), 0.1, canvas)
    # nail_positions must have shape (N, 2)
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 0, np.zeros((10, 3)), 0.1, canvas)
    # string strength must be >0
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 1, nail_positions, -1.0, canvas)
    # picture must have ndim==2
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 0, nail_positions, 0.1, np.zeros((1, 1, 1)))
    # picture must be in the [0, 1] range
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 0, nail_positions, 0.1, np.arange(0, 10).reshape((-1, 2)))
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_with_cache(0, 0, nail_positions, 0.1, np.arange(-10, 1).reshape((-1, 2)))

# ---------------- get_aa_line_no_cache ----------------
def test_get_aa_line_no_cache_invalid_args():
    nail_positions = np.array([[0, 0], [1, 1]])
    canvas = np.ones((5, 5))
    # from_idx must be an int
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache("not an int", 0, nail_positions, 0.1, canvas)
    # to_idx must be an int
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, "not an int", nail_positions, 0.1, canvas)
    # positions must be an array
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 1, "not an array", 0.1, canvas)
    # string_strength must be a float
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 1, nail_positions, "not a float", canvas)
    # canvas must be an array
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 1, nail_positions, 0.1, "not an array")
    # idx must not be out of range
    with pytest.raises(IndexError):
        pathfinding.get_aa_line_no_cache(0, 5, nail_positions, 0.1, canvas)
    # nail_positions must have ndim==2
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 0, np.arange(10), 0.1, canvas)
    # nail_positions must have shape (N, 2)
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 0, np.zeros((10, 3)), 0.1, canvas)
    # string strength must be >0
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 1, nail_positions, -1.0, canvas)
    # picture must have ndim==2
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 0, nail_positions, 0.1, np.zeros((1, 1, 1)))
    # picture must be in the [0, 1] range
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 0, nail_positions, 0.1, np.arange(0, 10).reshape((-1, 2)))
    with pytest.raises(ValueError):
        pathfinding.get_aa_line_no_cache(0, 0, nail_positions, 0.1, np.arange(-10, 1).reshape((-1, 2)))

# ---------------- get_next_nail_position ----------------
def test_get_next_nail_position_invalid_args():
    shape = (10, 10)
    canvas = np.ones(shape)
    num_nails = 10
    nail_positions = np.arange(num_nails*2).reshape((-1, 2))
    original_img = np.zeros(shape)
    should_skip_function = lambda i,j: False

    # current nail idx must be int
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position("not an int", canvas, nail_positions, original_img, 0.1, should_skip_function)
    # canvas must be an array
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, "not an array", nail_positions, original_img, 0.1, should_skip_function)
    # nail positions must be an array
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, "not an array", original_img, 0.1, should_skip_function)
    # original img must be an array
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, "not an array", 0.1, should_skip_function)
    # string strength must be a float
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, original_img, "not a float", should_skip_function)
    # should_skip_function must be callable
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, original_img, 0.1, "not a callable")
    # cache lines must be bool
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, original_img, 0.1, "rectangle", cache_lines = "not a bool")

    # current nail index must be in valid range
    with pytest.raises(IndexError):
        pathfinding.get_next_nail_position(-1, canvas, nail_positions, original_img, 0.1, should_skip_function)
    with pytest.raises(IndexError):
        pathfinding.get_next_nail_position(len(nail_positions)+1, canvas, nail_positions, original_img, 0.1, should_skip_function)
    # canvas must be a 2D array
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, np.zeros((2, 2, 2)), nail_positions, original_img, 0.1, should_skip_function)
    # canvas must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, np.arange(-10, 0).reshape((-1, 2)), nail_positions, original_img, 0.1, should_skip_function)
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, np.arange(0, 10).reshape((-1, 2)), nail_positions, original_img, 0.1, should_skip_function)
    # nail positions must be a 2D array
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, np.zeros((2, 2, 2)), original_img, 0.1, should_skip_function)
    # nail positions must have 2 columns
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, np.zeros((20, 3)), original_img, 0.1, should_skip_function)
    # original img must be a 2D array
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, np.zeros((2, 2, 2)), 0.1, should_skip_function)
    # original img must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, np.arange(-10, 0).reshape((-1, 2)), 0.1, "rectangle")
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, np.arange(0, 10).reshape((-1, 2)), 0.1, "rectangle")
    # string strength must be positive
    with pytest.raises(ValueError):
        pathfinding.get_next_nail_position(0, canvas, nail_positions, original_img, -1, "rectangle")
    

def test_get_next_nail_position_circle_layout():
    shape = (20, 20)
    canvas = np.ones(shape, dtype=float)
    nail_positions = np.array([[0, 10], [10, 19], [19, 10], [10, 0]])
    original_img = np.zeros(shape, dtype=float)
    should_skip_function = lambda i,j: False

    
    best_idx, new_canvas, distance, improvement = pathfinding.get_next_nail_position(
        current_nail_idx=0,
        canvas=canvas,
        nail_positions=nail_positions,
        original_img=original_img,
        string_strength=0.5,
        should_skip_function=should_skip_function
    )
    # We should get a valid next nail (not None) and some improvement (> -1)
    assert best_idx is not None
    assert new_canvas is not None
    assert distance >= 0
    assert improvement >= 0

def test_get_next_nail_position_rectangle_layout():
    shape = (20, 20)
    canvas = np.ones(shape, dtype=float)
    nail_positions = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    original_img = np.zeros(shape, dtype=float)
    should_skip_function = lambda i,j: False
    
    best_idx, new_canvas, distance, improvement = pathfinding.get_next_nail_position(
        current_nail_idx=0,
        canvas=canvas,
        nail_positions=nail_positions,
        original_img=original_img,
        string_strength=0.5,
        should_skip_function=should_skip_function
    )
    # We should get a valid next nail (not None) and some improvement (> -1)
    assert best_idx is not None
    assert new_canvas is not None
    assert distance >= 0
    assert improvement >= 0

# ---------------- get_optimal_string_path ----------------

def test_get_optimal_string_path_invalid_args():
    shape = (10, 10)
    canvas = np.ones(shape)
    num_nails = 10
    nail_positions = np.arange(num_nails*2).reshape((-1, 2))
    nail_angles = np.arange(num_nails)
    original_img = np.zeros(shape)
    # canvas must be an array
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path("not an array", nail_positions, original_img, 0.1, 10, "rectangle")
    # nail positions must be an array
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, "not an array", original_img, 0.1, 10, "rectangle")
    # original img must be an array
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, "not an array", 0.1, 10, "rectangle")
    # string strength must be a float
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, "not a float", 10, "rectangle")
    # max num iter must be an int
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, "not an int", "rectaangle")
    # nail layout must be circle or rectangle
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "triangle")
    # nail angles cannot be None with circle layout
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", None)
    # nail angles must be an array with circle layout
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", "not an array")
    # nail angles and nail positions must have matching lengths with circle layout
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", np.arange(len(nail_positions)+1))
    # min angle diff cannot be None with circle layout
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, None)
    # min angle diff must be float with circle layout
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, "not a float")
    # cache lines must be bool
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "rectangle", cache_lines = "not a bool")


    # canvas must be a 2D array
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(np.arange(10), nail_positions, original_img, 0.1, 10, "rectangle")
    # canvas must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(np.arange(-10, 0).reshape((-1, 2)), nail_positions, original_img, 0.1, 10, "rectangle")
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(np.arange(0, 10).reshape((-1, 2)), nail_positions, original_img, 0.1, 10, "rectangle")
    # nail positions must be a 2D array
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, np.zeros((2, 2, 2)), original_img, 0.1, 10, "rectangle")
    # nail positions must have 2 columns
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, np.zeros((20, 3)), original_img, 0.1, 10, "rectangle")
    # original img must be a 2D array
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, np.zeros((2, 2, 2)), 0.1, 10, "rectangle")
    # original img must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, np.arange(-10, 0).reshape((-1, 2)), 0.1, 10, "rectangle")
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, np.arange(0, 10).reshape((-1, 2)), 0.1, 10, "rectangle")
    # string strength must be positive
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, -1, 10, "rectangle")
    # max num iter must be >0
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 0, "rectangle")
    # nail angles must be a 1D array with circle layout
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", np.zeros((10, 2)))
    # nail angles and nail positions must have matching lengths with circle layout
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", np.arange(len(nail_positions)+1))
    # min angle diff must be in [0, 2pi] range
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, -1)
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, 100)
    # patience must be >=0
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "rectangle", patience=-1)
    # epsilon must be >0
    with pytest.raises(ValueError):
        pathfinding.get_optimal_string_path(canvas, nail_positions, original_img, 0.1, 10, "rectangle", epsilon=0)


def test_get_optimal_string_path_runs():
    shape = (30, 30)
    num_nails = 4
    canvas = np.ones(shape)
    nail_positions = np.array([[0, 15], [15, 29], [29, 15], [15, 0]])
    nail_angles = np.linspace(0, 2*np.pi, num_nails, endpoint=False)
    original_img = np.zeros(shape)

    order, final_canvas, distances = pathfinding.get_optimal_string_path(
        canvas=canvas,
        nail_positions=nail_positions,
        original_img=original_img,
        string_strength=0.5,
        max_num_iter=10,
        nail_layout="circle",
        nail_angles=nail_angles
    )

    assert len(order) > 0
    assert final_canvas.shape == shape
    assert distances[0] >= distances[-1]  # should not get worse