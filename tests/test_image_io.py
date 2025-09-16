import numpy as np
import pytest
from stringart import image_io
from PIL import Image
from pathlib import Path

# ---------------- open_image ----------------
def test_open_image_file_not_found():
    # path must point to an existing image
    with pytest.raises(FileNotFoundError):
        image_io.open_image("nonexistent.png")


def test_open_image_valid(tmp_path):
    # check known image is opened correctly
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    path = tmp_path / "test.png"
    Image.fromarray(img).save(path)
    out = image_io.open_image(path)
    assert out.shape == (10, 10, 3)

def test_open_image_file_not_found_path(tmp_path):
    p = Path(tmp_path) / "file.png"
    with pytest.raises(FileNotFoundError):
        image_io.open_image(p)

# ---------------- replace_transparent_background ----------------
def test_replace_transparent_background_valid():
    # check transparent background is replaced correctly
    img = np.zeros((5, 5, 4), dtype=np.uint8)
    img[:, :, 3] = 128  # semi-transparent
    bg_color = (100, 150, 200)
    out = image_io.replace_transparent_background(img, bg_color)
    assert out.shape == (5, 5, 3)
    assert np.all((0 <= out) & (out <= 255))


def test_replace_transparent_background_invalid():
    img = np.zeros((5, 5, 3), dtype=np.uint8)
    # img must have shape (H, W, 4)
    with pytest.raises(ValueError):
        image_io.replace_transparent_background(img)
    with pytest.raises(ValueError):
        image_io.replace_transparent_background(np.zeros((5, 5), dtype=np.uint8))
    # background RGB must contain 3 int
    with pytest.raises(ValueError):
        image_io.replace_transparent_background(np.zeros((5, 5, 4)), (1, 2))
    # RGB values must be in the [0, 255] range
    with pytest.raises(ValueError):
        image_io.replace_transparent_background(np.zeros((5, 5, 4)), (1, 2, 999))


# ---------------- open_grayscale_crop_fixbg_img ----------------
def test_open_grayscale_crop_fixbg_img_rectangle(tmp_path):
    # check img is preprocessed correctly
    img = np.ones((10, 20, 3), dtype=np.uint8) * 255
    path = tmp_path / "rect.png"
    Image.fromarray(img).save(path)
    out = image_io.open_grayscale_crop_fixbg_img(str(path), (50, 50, 50), "rectangle")
    assert out.ndim == 2
    assert out.shape == (10, 20)


def test_open_grayscale_crop_fixbg_img_circle(tmp_path):
    # check correct preprocess + square center crop
    img = np.ones((20, 30), dtype=np.uint8) * 255
    path = tmp_path / "circ.png"
    Image.fromarray(img).save(path)
    out = image_io.open_grayscale_crop_fixbg_img(str(path), (50, 50, 50), "circle")
    assert out.shape[0] == out.shape[1]  # cropped square


def test_open_grayscale_crop_fixbg_img_invalid_layout(tmp_path):
    # layout must be circle or rectangle only
    img = np.ones((10, 10), dtype=np.uint8) * 255
    path = tmp_path / "img.png"
    Image.fromarray(img).save(path)
    with pytest.raises(ValueError):
        image_io.open_grayscale_crop_fixbg_img(str(path), (50, 50, 50), "triangle")


# ---------------- from_string_idx_order_to_image_array ----------------
def test_from_string_idx_order_to_image_array_invalid_strength():
    # string strength must be >0
    with pytest.raises(ValueError):
        image_io.from_string_idx_order_to_image_array([0, 1], (10, 10), "circle", 5, -0.5)


def test_from_string_idx_order_to_image_array_invalid_order():
    # string idx order must contain >=2 elements
    with pytest.raises(ValueError):
        image_io.from_string_idx_order_to_image_array([0], (10, 10), "circle", 5, 0.1)


# ---------------- resolve_output_path ----------------
def test_resolve_output_path_with_file(tmp_path):
    # check files are saved in the correct path
    file_path = tmp_path / "out.png"
    result = image_io.resolve_output_path(file_path, "default.png", [".png", ".jpg"])
    assert result == file_path


def test_resolve_output_path_with_folder(tmp_path):
    # check png files are saved correctly
    result = image_io.resolve_output_path(tmp_path, "default.png", [".png"])
    assert result.suffix == ".png"


def test_resolve_output_path_invalid_default():
    # default name cannot be empty
    with pytest.raises(ValueError):
        image_io.resolve_output_path("out", "", [".png"])