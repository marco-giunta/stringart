# StringArt - Quick Usage Guide
Main algorithm and package name based on [kaspar98/StringArt](https://github.com/kaspar98/StringArt), rewritten from scratch with performance and usability in mind.

**Improved/extra features**:
- `pip` installable python package
- multiple interfaces available: python API, CLI, Shiny WebApp UI (experimental)
- improved performance thanks to caching, internal downscaling & some other tricks
- improved usability: reparametrized algorithm to allow for a more intuitive and precise control of the output image

## StringArt description
*StringArt* lets you approximate an input image using a single continuous string looped around nails on the border of a canvas (see the documentation for an explanation of how the algorithm works).
You can run it in three ways:

- Python API: call the functions directly in your own code or jupyter notebook.
- Command-Line Interface (CLI): run the tool from the terminal.
- Shiny WebApp: start the webapp from the terminal, then interact with the GUI using your browser (experimental).

```{toctree}
installation
quickstart
parameters_cheatsheet
```