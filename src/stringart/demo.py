import importlib.resources as pkg_resources
from . import data
from pathlib import Path

def list_demo_images_paths():
    """List paths of available demo images contained in stringart.data.demo_img.

    Returns
    -------
    demo_images_path_list : list of path
        List containing the paths of the available demo images.
    """
    demo_img_dir = pkg_resources.files(data) / "demo_img"
    return [p for p in demo_img_dir.iterdir() if p.suffix.lower() in [".png", ".jpg", ".jpeg"]]

def list_demo_images():
    """List file names of available demo images contained in stringart.data.demo_img.

    Returns
    -------
    demo_images_names_list : list of str
        List containing the file names of the available demo images.
    """
    return [img.name for img in list_demo_images_paths()]

def get_demo_image_path(filename : str = "einstein.jpg"):
    """Get the path of one of the available stringart.data.demo_img to be opened using stringart.image_io.

    Parameters
    ----------
    filename : str
        Name of the files output by stringart.demo.list_demo_images().
    
    Returns
    -------
    filepath : path
        Path of the chosen demo image file.
    """
    if filename not in list_demo_images():
        raise ValueError(f"`filename` must be in {list_demo_images()}; got {filename} instead")
    
    return pkg_resources.files(data) / "demo_img" / filename