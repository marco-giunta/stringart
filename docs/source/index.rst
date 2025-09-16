.. stringart documentation master file, created by
   sphinx-quickstart on Mon Sep 15 19:49:44 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to *StringArt*'s documentation!
=======================================

*StringArt* lets you approximate an input image using a single continuous string looped around nails on the border of a canvas (see the documentation for an explanation of how the algorithm works).
You can run it in three ways:

- Python API: call the functions directly in your own code or jupyter notebook.
- Command-Line Interface (CLI): run the tool from the terminal.
- Shiny WebApp: start the webapp from the terminal, then interact with the GUI using your browser (experimental).

Main algorithm and package name based on `kaspar98/StringArt <https://github.com/kaspar98/StringArt>`_, rewritten from scratch with performance and usability in mind.

**Improved/extra features**:

- `pip` installable python package
- multiple interfaces available: python API, CLI, Shiny WebApp UI (experimental)
- improved performance thanks to caching, internal downscaling & some other tricks
- improved usability: reparametrized algorithm to allow for a more intuitive and precise control of the output image

.. toctree::
   :maxdepth: 4
   :caption: Tutorials

   tutorials/quickstart_guide/quickstart_guide
   tutorials/parameters_guide/parameters_guide
   tutorials/preprocessing_tips/preprocessing_tips

.. toctree::
   :maxdepth: 1
   :caption: Technical info

   technical_info/algorithm_technical_breakdown
   technical_info/caching_performance_benchmark

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   stringart