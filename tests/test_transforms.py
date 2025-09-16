import numpy as np
import pytest
from stringart import transforms

# ----------------- center_square_crop -----------------
def test_center_square_crop_basic():
    img = np.arange(12).reshape((3, 4))
    cropped = transforms.center_square_crop(img)
    # check it crops out the correct image portions
    assert cropped.shape == (3, 3)
    assert np.array_equal(cropped, img[:, :3])

def test_center_square_crop_non_2d():
    img = np.zeros((3, 4, 3))
    # img should be a 2D array
    with pytest.raises(ValueError):
        transforms.center_square_crop(img)

def test_center_square_crop_invalid_input():
    # img should be an array
    with pytest.raises(ValueError):
        transforms.center_square_crop("not an array")

# ----------------- rgb2gray -----------------
def test_rgb2gray_basic():
    img = np.ones((4, 4, 3))
    gray = transforms.rgb2gray(img)
    # grayscale img should have no RGB channel axis & be in the [0, 1] range
    assert gray.shape == (4, 4)
    assert np.all(gray >= 0) and np.all(gray <= 1)

def test_rgb2gray_invalid_input():
    img = np.ones((4, 4))  
    # ignore already grayscale images
    with pytest.raises(ValueError):
        transforms.rgb2gray(img)
    img = "not an array"
    # img should be an array
    with pytest.raises(ValueError):
        transforms.rgb2gray(img)

# ----------------- downscale -----------------
def test_downscale_basic():
    img = np.ones((10, 10))
    down = transforms.downscale(img, 0.5)
    expected_shape = (5, 5)
    # check it gives the correct downscaled shape up to 1px approximation errors
    assert down.shape == expected_shape or all(abs(a - b) <= 1 for a, b in zip(down.shape, expected_shape)) # allow for 1 px difference due to rounding
    assert np.all(down >= 0) and np.all(down <= 1)

def test_downscale_invalid_factor():
    img = np.ones((10, 10))
    # downscale factor must be >0
    with pytest.raises(ValueError):
        transforms.downscale(img, 0)
    with pytest.raises(ValueError):
        transforms.downscale(img, -10)
    # downscale factor must be <=1
    with pytest.raises(ValueError):
        transforms.downscale(img, 1.5)
    # downscale factor must be a number
    with pytest.raises(ValueError):
        transforms.downscale(img, "not a number")