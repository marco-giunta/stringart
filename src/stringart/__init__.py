from . import (
    cli,
    canvas,
    image_io,
    pathfinding,
    pathfinding_precache,
    skip,
    transforms,
    demo
)

from .main import create_stringart
from .animate import animate_stringart

__all__ = [
    "cli",
    "canvas",
    "demo",
    "image_io",
    "pathfinding",
    "pathfinding_precache",
    "skip",
    "transforms",
    "create_stringart",
    "animate_stringart",
]

from importlib.util import find_spec

if find_spec("shiny") is not None:
    from .ui import stringart_app
    __all__.append("stringart_app")

from importlib.metadata import version
__version__ = version("stringart")