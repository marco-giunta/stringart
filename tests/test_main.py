import numpy as np
import pytest
from PIL import Image
from stringart.main import create_stringart

def test_create_stringart_circle(tmp_path):
    # create dummy grayscale image
    img = np.ones((10, 10, 3), dtype=np.uint8) * 255
    path = tmp_path / "img.png"
    Image.fromarray(img).save(path)

    idxs, canvas, dist = create_stringart(
        img_path=str(path),
        num_nails=10,
        downscale_factor=1.0,
        max_num_iter=5,
        nail_layout="circle"
    )
    assert isinstance(idxs, np.ndarray)
    assert isinstance(canvas, np.ndarray)
    assert isinstance(dist, np.ndarray)
    assert canvas.shape == (10, 10)

def test_create_stringart_rectangle(tmp_path):
    # create dummy grayscale image
    img = np.ones((10, 10, 3), dtype=np.uint8) * 255
    path = tmp_path / "img.png"
    Image.fromarray(img).save(path)

    idxs, canvas, dist = create_stringart(
        img_path=str(path),
        num_nails=10,
        downscale_factor=1.0,
        max_num_iter=5,
        nail_layout="rectangle"
    )
    assert isinstance(idxs, np.ndarray)
    assert isinstance(canvas, np.ndarray)
    assert isinstance(dist, np.ndarray)
    assert canvas.shape == (10, 10)

@pytest.fixture
def dummy_img_path(tmp_path):
    """Fixture: create a simple 10x10 white RGB image and return its path."""
    path = tmp_path / "dummy.png"
    img = np.ones((10, 10, 3), dtype=np.uint8) * 255
    Image.fromarray(img).save(path)
    return str(path)


def test_invalid_img_path_type(dummy_img_path):
    with pytest.raises(ValueError, match="`img_path` must be str"):
        create_stringart(
            img_path=123,  # not a string
            num_nails=10,
            downscale_factor=1.0,
        )


def test_invalid_num_nails(dummy_img_path):
    with pytest.raises(ValueError, match="`num_nails` must be int"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails="ten",  # wrong type
            downscale_factor=1.0,
        )

    with pytest.raises(ValueError, match="`num_nails` must be int >= 10"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails=2,  # too few nails
            downscale_factor=1.0,
        )


@pytest.mark.parametrize("factor", [0, 1.5, -0.1, "bad"])
def test_invalid_downscale_factor(dummy_img_path, factor):
    with pytest.raises(ValueError, match="`downscale_factor`"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails=10,
            downscale_factor=factor,
        )


@pytest.mark.parametrize("strength", [0, -0.5, "strong"])
def test_invalid_string_strength(dummy_img_path, strength):
    with pytest.raises(ValueError, match="`string_strength`"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails=10,
            downscale_factor=1.0,
            string_strength=strength,
        )


def test_invalid_nail_layout(dummy_img_path):
    with pytest.raises(ValueError, match="`nail_layout`"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails=10,
            downscale_factor=1.0,
            nail_layout="triangle",  # unsupported
        )


def test_invalid_background_color(dummy_img_path):
    # Wrong type
    with pytest.raises(ValueError, match="`background_color` must be a tuple/list"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails=10,
            downscale_factor=1.0,
            background_color="gray",
        )

    # Wrong length
    with pytest.raises(ValueError, match="must be a tuple/list of 3"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails=10,
            downscale_factor=1.0,
            background_color=(255, 255),  # only 2 channels
        )

    # Out of range
    with pytest.raises(ValueError, match="ints in"):
        create_stringart(
            img_path=dummy_img_path,
            num_nails=10,
            downscale_factor=1.0,
            background_color=(0, 0, 999),  # invalid value
        )