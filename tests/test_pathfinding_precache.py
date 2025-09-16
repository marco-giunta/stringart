import numpy as np
import pytest
from stringart import pathfinding_precache, skip, canvas

# ---------------- precache_lines ----------------
def test_precache_lines_invalid_args():
    nail_positions = np.arange(20).reshape((-1, 2))
    canvas_shape = (20, 20)
    should_skip = skip.get_should_skip_function("rectangle", nail_positions)
    # nail positions must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines("not an array", 0.1, canvas_shape, should_skip)
    # string strength must be a float
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(nail_positions, "not a float", canvas_shape, should_skip)
    # canvas shape must be a tuple or list
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(nail_positions, 0.1, "not a tuple or list", should_skip)
    # canvas shape must be a tuple or list of int
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(nail_positions, 0.1, ("not an int", "not an int", "not an int"), should_skip)
    # canvas shape must contain only positive int
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(nail_positions, 0.1, (-1, 0.1), should_skip)
    # canvas shape must contain only 2 elements
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(nail_positions, 0.1, (2, 2, 2), should_skip)
    # should skip must be callable
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(nail_positions, 0.1, canvas_shape, "not a callable")

    # nail positions must have ndim==2
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(np.arange(10), 0.1, canvas_shape, should_skip)
    # nail positions must have shape (N, 2)
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(np.zeros((10, 3)), 0.1, canvas_shape, should_skip)
    # string strength must be >0
    with pytest.raises(ValueError):
        pathfinding_precache.precache_lines(nail_positions, -1, canvas_shape, should_skip)

# ---------------- get_aa_line_from_precache ----------------
def test_get_aa_line_from_precache_invalid_args():
    canvas_shape = (20, 20)
    num_nails = 20
    picture, nail_positions, _ = canvas.create_canvas_and_nail_positions(canvas_shape, "rectangle", num_nails)
    should_skip = skip.get_should_skip_function("rectangle", nail_positions)
    line_cache_dict = pathfinding_precache.precache_lines(nail_positions, 0.1, canvas_shape, should_skip)
    # from_idx must be an int
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache("not an int", 1, picture, 0.1, line_cache_dict)
    # to_idx must be an int
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, "not an int", picture, 0.1, line_cache_dict)
    # picture must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, 1, "not an array", 0.1, line_cache_dict)
    # string strength must be a float
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, 1, picture, "not a float", line_cache_dict)
    # line cache dict must be a dict
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, 1, picture, 0.1, "not a dict")

    # from_idx must be >=0
    with pytest.raises(IndexError):
        pathfinding_precache.get_aa_line_from_precache(-1, 0, picture, 0.1, line_cache_dict)
    # to_idx must be >=0
    with pytest.raises(IndexError):
        pathfinding_precache.get_aa_line_from_precache(0, -1, picture, 0.1, line_cache_dict)
    # picture must have ndim==2
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, 0, np.zeros((1, 1, 1)), 0.1, line_cache_dict)
    # picture must be in the [0, 1] range
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, 0, np.arange(0, 10).reshape((-1, 2)), 0.1, line_cache_dict)
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, 0, np.arange(-10, 1).reshape((-1, 2)), 0.1, line_cache_dict)
    # string strength must be >0
    with pytest.raises(ValueError):
        pathfinding_precache.get_aa_line_from_precache(0, 1, picture, 0, line_cache_dict)

# ---------------- get_next_nail_position_precache ----------------
def test_get_next_nail_position_precache_invalid_args():
    canvas_shape = (20, 20)
    num_nails = 20
    current_canvas, nail_positions, _ = canvas.create_canvas_and_nail_positions(canvas_shape, "rectangle", num_nails)
    should_skip = skip.get_should_skip_function("rectangle", nail_positions)
    line_cache_dict = pathfinding_precache.precache_lines(nail_positions, 0.1, canvas_shape, should_skip)
    original_img = np.zeros(canvas_shape)
    # current nail idx must be an int
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache("not an int", current_canvas, nail_positions, original_img, 0.1, line_cache_dict)
    # current canvas must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, "not an array", nail_positions, original_img, 0.1, line_cache_dict)
    # nail positions must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, "not an array", original_img, 0.1, line_cache_dict)
    # original img must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, nail_positions, "not an array", 0.1, line_cache_dict)
    # string strength must be a float
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, nail_positions, original_img, "not a float", line_cache_dict)
    # line cache dict must be a dict
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, current_canvas, nail_positions, original_img, 0.1, "not a dict")

    # current nail index must be in valid range
    with pytest.raises(IndexError):
        pathfinding_precache.get_next_nail_position_precache(-1, current_canvas, nail_positions, original_img, 0.1, line_cache_dict)
    with pytest.raises(IndexError):
        pathfinding_precache.get_next_nail_position_precache(len(nail_positions)+1, current_canvas, nail_positions, original_img, 0.1, line_cache_dict)
    # canvas must be a 2D array
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, np.zeros((2, 2, 2)), nail_positions, original_img, 0.1, line_cache_dict)
    # canvas must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, np.arange(-10, 0).reshape((-1, 2)), nail_positions, original_img, 0.1, line_cache_dict)
    # nail positions must be a 2D array
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, np.zeros((2, 2, 2)), original_img, 0.1,  line_cache_dict)
    # nail positions must have 2 columns
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, np.zeros((20, 3)), original_img, 0.1, line_cache_dict)
    # original img must be a 2D array
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, nail_positions, np.zeros((2, 2, 2)), 0.1, line_cache_dict)
    # original img must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, nail_positions, np.arange(-10, 0).reshape((-1, 2)), 0.1, line_cache_dict)
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, nail_positions, np.arange(0, 10).reshape((-1, 2)), 0.1, line_cache_dict)
    # string strength must be positive
    with pytest.raises(ValueError):
        pathfinding_precache.get_next_nail_position_precache(0, canvas, nail_positions, original_img, -1, line_cache_dict)
    
def test_get_next_nail_position_precache_circle_layout():
    pass # TODO

def test_get_next_nail_position_precache_rectangle_layout():
    pass # TODO

# ---------------- get_optimal_string_path_precache ----------------
def test_get_optimal_string_path_precache_invalid_args():
    shape = (10, 10)
    canvas = np.ones(shape)
    num_nails = 10
    nail_positions = np.arange(num_nails*2).reshape((-1, 2))
    nail_angles = np.arange(num_nails)
    original_img = np.zeros(shape)

    # canvas must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache("not an array", nail_positions, original_img, 0.1, 10, "rectangle")
    # nail positions must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, "not an array", original_img, 0.1, 10, "rectangle")
    # original img must be an array
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, "not an array", 0.1, 10, "rectangle")
    # string strength must be a float
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, "not a float", 10, "rectangle")
    # max num iter must be an int
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, "not an int", "rectaangle")
    # nail layout must be circle or rectangle
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "triangle")
    # nail angles cannot be None with circle layout
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", None)
    # nail angles must be an array with circle layout
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", "not an array")
    # nail angles and nail positions must have matching lengths with circle layout
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", np.arange(len(nail_positions)+1))
    # min angle diff cannot be None with circle layout
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, None)
    # min angle diff must be float with circle layout
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, "not a float")
    
    # canvas must be a 2D array
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(np.arange(10), nail_positions, original_img, 0.1, 10, "rectangle")
    # canvas must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(np.arange(-10, 0).reshape((-1, 2)), nail_positions, original_img, 0.1, 10, "rectangle")
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(np.arange(0, 10).reshape((-1, 2)), nail_positions, original_img, 0.1, 10, "rectangle")
    # nail positions must be a 2D array
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, np.zeros((2, 2, 2)), original_img, 0.1, 10, "rectangle")
    # nail positions must have 2 columns
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, np.zeros((20, 3)), original_img, 0.1, 10, "rectangle")
    # original img must be a 2D array
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, np.zeros((2, 2, 2)), 0.1, 10, "rectangle")
    # original img must be in [0, 1] range
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, np.arange(-10, 0).reshape((-1, 2)), 0.1, 10, "rectangle")
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, np.arange(0, 10).reshape((-1, 2)), 0.1, 10, "rectangle")
    # string strength must be positive
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, -1, 10, "rectangle")
    # max num iter must be >0
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 0, "rectangle")
    # nail angles must be a 1D array with circle layout
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", np.zeros((10, 2)))
    # nail angles and nail positions must have matching lengths with circle layout
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", np.arange(len(nail_positions)+1))
    # min angle diff must be in [0, 2pi] range
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, -1)
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "circle", nail_angles, 100)
    # patience must be >=0
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "rectangle", patience=-1)
    # epsilon must be >0
    with pytest.raises(ValueError):
        pathfinding_precache.get_optimal_string_path_precache(canvas, nail_positions, original_img, 0.1, 10, "rectangle", epsilon=0)

def test_get_optimal_string_path_precache_runs():
    pass # TODO