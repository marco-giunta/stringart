# `stringart` python package
[![tests](https://github.com/marco-giunta/stringart/actions/workflows/stringart_tests.yml/badge.svg)](https://github.com/marco-giunta/stringart/actions/workflows/stringart_tests.yml)
[![docs](https://github.com/marco-giunta/stringart/actions/workflows/stringart_docs_gh_pages.yml/badge.svg)](https://github.com/marco-giunta/stringart/actions/workflows/stringart_docs_gh_pages.yml)
## *StringArt* description
*StringArt* lets you approximate an input image using a single continuous string looped around nails on the border of a canvas (see the documentation for an explanation of how the algorithm works).
You can run it in three ways:

- Python API: call the functions directly in your own code or jupyter notebook.
- Command-Line Interface (CLI): run the tool from the terminal.
- Shiny WebApp: start the webapp from the terminal, then interact with the GUI using your browser (experimental).

Main algorithm and package name based on [kaspar98/StringArt](https://github.com/kaspar98/StringArt), rewritten from scratch with performance and usability in mind.

**Improved/extra features**:
- `pip` installable python package
- multiple interfaces available: python API, CLI, Shiny WebApp UI (experimental)
- improved performance thanks to caching, internal downscaling & some other tricks
- improved usability: reparametrized algorithm to allow for a more intuitive and precise control of the output image

Please check out [`stringart`'s online documentation](https://marco-giunta.github.io/stringart/) to read detailed installation and usage instructions; otherwise keep reading to get started quickly!

## Installation
### Virtual environment (optional)
It's recommended to install and run *StringArt* in a separate virtual environment, using the tool of your choice.

For example using python's default `venv`:
1) create the virtual environment:
    ```
    python -m venv stringart-venv
    ```
2) activate the virtual environment:

    *Linux/macOS*:
    ```
    source stringart-env/bin/activate
    ```
    *Windows*:
    ```
    stringart-env\Scripts\activate
    ```
3) to deactivate the virtual environment:
    ```
    deactivate
    ```

You can also use other tools, like e.g. `conda`:
```
conda create --name stringart-env python=3.11
conda activate stringart-env
```


### Installation types
(If unsure, choose whether or not you want the optional experimental GUI, then use the corresponding `pip install ...` command)
#### Standard install (API+CLI):

- Direct install from GitHub:
    ```
    pip install git+https://github.com/marco-giunta/stringart.git
    ```
- Otherwise you can clone the repository and install as follows:
    ```
    cd <path where you want to git clone>
    git clone https://github.com/marco-giunta/stringart.git
    cd stringart
    pip install .
    ```

#### Optional GUI install (shiny WebApp, experimental):
- Direct install from GitHub:
    ```
    pip install "git+https://github.com/marco-giunta/stringart.git#egg=stringart[ui]"
    ```
- Alternative git clone install:
    ```
    cd <path where you want to git clone>
    git clone https://github.com/marco-giunta/stringart.git
    cd stringart
    pip install stringart[ui]
    ```

#### Install & run tests
- Direct install from GitHub:
    ```
    pip install "git+https://github.com/marco-giunta/stringart.git#egg=stringart[test]"
    ```

- Alternative git clone install:
    ```
    cd <path where you want to git clone>
    git clone https://github.com/marco-giunta/stringart.git
    cd stringart
    pip install .[test]
    ```
- You can then run tests using:
    ```
    pytest
    ```

#### Install both UI & test optional addons
- Direct install from GitHub:
    ```
    pip install "git+https://github.com/<your-username>/stringart.git#egg=stringart[ui,test]"
    ```
- Alternative git clone install:
    ```
    cd <path where you want to git clone>
    git clone https://github.com/marco-giunta/stringart.git
    cd stringart
    pip install .[ui,test]
    ```

#### Developer installation
To work on the code clone the repo, then install in editable mode:
```
cd <path where you want to git clone>
git clone https://github.com/marco-giunta/stringart.git
cd stringart
pip install -e .[test,ui]
```

## Quickstart

### Python API (code-based)
```
from stringart import create_stringart
from stringart.image_io import save_stringart

# Generate string art
order, canvas, distances = create_stringart(
    img_path="input.png",
    num_nails=250,
    downscale_factor=0.3,
)

# Save the output
save_stringart(canvas, "output.png")
```
- `order`: sequence of nail indices visited by the string
- `canvas`: final grayscale image (values in `[0, 1]`)
- `distances`: error progression at each iteration ($L_2$ norm)

Please read the documentation to learn about the available arguments/modules/functions.

### CLI (text-based)
- Open the terminal and enter:
    ```
    stringart -i input.png -o output.png -n 250 -d 0.3
    ```
- You can also save the other outputs:
    ```
    # Save nail order and error progression
    stringart -i input.png -o output.png --string_order order.txt --distance dist.txt
    ```
- You can modify any parameter value by passing it as
    ```
    stringart -short_parameter_name value
    ```
    or 
    ```
    stringart --long_parameter_name value
    ```

- To see a short description of all parameters enter:
    ```
    stringart -h
    ```
    or 
    ```
    stringart --help
    ```

### Shiny WebApp (UI-based)
#### Starting the WebApp
- If the optional packages have been installed, open the terminal and run:
    ```
    stringart-ui
    ```
    The terminal should then print something like
    ```
    INFO:     Started server process [707]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    ```
- Click on that `http://127.0.0.1:8000` link (depending on your terminal app you may need to do something like CTRL+click) or copy/paste it into your browser of choice.

- Once you're done, close the browser tab, go back to the terminal and press CTRL+C.

#### Using the WebApp
- To use the webapp upload your image (or use a demo one), tweak the parameter values using the sidebar menu, and view your output in the output tab.
- The webapp also has a "help" section you can read to learn every detail about how to set each parameter without needing to read the documentation or the rest of this readme; there are also some useful trick to ensure optimal visual accuracy in the result.
- This is the recommended option for non technical users, but please note that webapp support is still experimental; there are some known bugs (see the webapp's help section) and some functionality is missing, so using the API or the CLI may be unavoidable for some users.

## Parameters cheatsheet
Here's a complete list of the parameters you can set from python or the CLI. Notice that for the CLI you can either use the short form (e.g. `-i`) or the long form (e.g. `--input`) for the parameter names.

More details are available in the docs, or in the webapp's help section (along with some tips to ensure good visual quality).


| Parameter (API)    | CLI flag                  | Type                | Default      | Description                                                                                                                                          |
| ------------------ | ------------------------- | ------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `img_path`         | `-i, --input`             | str (path)          | **Required** | Path to input image (`.png`, `.jpg`, `.jpeg`, `.pdf`). Auto-grayscaled; cropped if `circle` layout; transparent PNGs filled with `background_color`. |
| `num_nails`        | `-n, --nails`             | int                 | **Required** | Number of nails on the border. More nails = higher detail but slower. Try increasing it by ~50-100 if circular ring artifacts appear with `layout=="circle"`. *Recommended*: typical values: 150–400. Don't go too much lower to ensure good visual quality, don't go too much higher to ensure good/stable performance + to avoid crashes due to insufficient RAM (unless caching is disabled).                                                              |
| `downscale_factor` | `-d, --downscale`         | float               | **Required** | Rescales image before processing to use a lower internal resolution → speed up computations. Lower → faster, coarser; higher → slower, sharper. *Recommended*: choose a value that causes your pic to go down to ~300-700px per side. Typical values: 0.25-0.5 (to halve or more pic size). Try increasing this if output visual quality is too low or if the algorithm stops too early compared to the input `maxiter`.                                                                 |
| `string_strength`  | `-s, --strength`          | float               | 0.1          | How much each line darkens the canvas. Higher → darker, thicker effect. *Recommended*: increase this if final image appears too white/empty, decrease if too dark/filled in. Typical values: 0.1-0.25 (don't go too much higher than this or the output will be a black mess).                                                                              |
| `max_num_iter`     | `-ni, --maxiter`          | int                 | 5000         | Maximum number of strings/iterations. Larger = more detail, slower. Early stopping may stop earlier.                                                 |
| `nail_layout`      | `-l, --layout`            | str                 | `"circle"`   | Nail arrangement: `"circle"` or `"rectangle"`. Circle recommended.                                                                                   |
| `cache_lines`      | `-nc, --no-cache`         | bool flag           | True (API), False (CLI)         | Cache line computations for speed. *Recommended*: disable caching only for debugging, i.e. always use the default values, unless you really want `num_nails` larger than ~800 and don't have enough RAM.                                                  |
| `precache_lines`   | `-npc, --no-precache`     | bool flag           | True (API), False (CLI)         | Precompute all line paths before starting (much faster at runtime, uses more memory). *Recommended*: leave precaching on, i.e. always use the default values, unless you really want `num_nails` larger than ~800 and don't have enough RAM.                                                                     |
| `min_angle_diff`   | `-mad, --min-angle-diff`  | float               | π/8 (≈0.39)  | Circle layout only. Minimum angular spacing (radians) between consecutive nails to avoid redundant/parallel lines.                                             |
| `background_color` | `-bc, --background-color` | tuple\[int,int,int] | (50, 50, 50) | RGB color (0–255). Used to replace transparency in PNGs.                                                                                             |
| `patience`         | `-p, --patience`          | int                 | 20           | Early stopping patience: number of stagnant iterations before halting.                                                                               |
| `epsilon`          | `-e, --epsilon`           | float               | 1e-6         | Early stopping tolerance: minimum error improvement considered significant.                                                                          |
| *(output path)*    | `-o, --output`            | str (path)          | None         | Where to save the generated image. Folder or file. Extensions: `.png`, `.jpg`, `.jpeg`, `.pdf`.                                                      |
| *(string order)*   | `-so, --string_order`     | str (path)          | None         | Save nail sequence to file (`.txt`).                                                                                                                 |
| *(distance vec)*   | `-ds, --distance`         | str (path)          | None         | Save error progression to file (`.txt`).                                                                                                             |

