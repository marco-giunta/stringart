# Installation
Installing *StringArt* is a two-step process:
1. activate a virtual environment (optional but recommended);
2. install one of the available `stringart` versions using `pip install ...`.

## Virtual environment (optional)
It's recommended to install and run *StringArt* in a separate virtual environment, using the tool of your choice; if instead you want to install `stringart` globally, skip this section and just use the relevant `pip install ...` command from the next section.

For example to activate the virtual environment using python's default `venv`:
1) create the virtual environment:
    ```
    python -m venv stringart-venv
    ```
2) activate the virtual environment:

    *Linux/macOS*:
    ```
    source stringart-venv/bin/activate
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
```
```
conda activate stringart-env
```

## Installation instructions
There are three ways to interact with *StringArt*:
- via python code directly, e.g. in a jupyter notebook (API);
- via the terminal (CLI);
- via the graphical user interface using the shiny WebApp (GUI).

### *Which version should I choose?*
- The graphical option is recommended for non technical users, but please be aware that extra dependencies are needed and that support is still experimental: there may be bugs that break an optional feature you need (start the webapp and read its "known bugs" section). If a feature you need is currently not working, please don't be afraid to use the CLI! Having said that, please know that the main features work just fine inside the webapp, so you may not actually need the CLI if you simply want to visualize the output obtained starting from an input/the parameter values of your choice.
- For a) technical users, and/or b) nontechnical users who need a `stringart` feature that's currently broken in the GUI, the CLI is the recommended approach; it's feature complete, and no extra dependencies are needed as the CLI is already part of the main package.
- The API is not the recommended way to interact with *StringArt* if all you care about is generating string art images given a specified input; use it if you want to access the actual python variables computed by `stringart`'s modules in order to use/explore them in your own code.

Below you can find two ways to install the package for each version. If you don't know what `git clone` does or you don't need to explicitly access the source code files, please use the relevant `pip install ...` command.

### Standard install (API+CLI):

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

### Optional GUI install (shiny WebApp, experimental):
- Direct install from GitHub:
    ```
    pip install "stringart[ui] @ git+https://github.com/marco-giunta/stringart.git"
    ```
- Alternative git clone install:
    ```
    cd <path where you want to git clone>
    git clone https://github.com/marco-giunta/stringart.git
    cd stringart
    pip install .[ui]
    ```

#### Install & run tests
*Remark*: the test suite itself is not included in the package distribution. To run tests, you must clone the repository so you have access to the `tests/` folder; simply using `pip install "stringart[test] @ git+https://github.com/marco-giunta/stringart.git"` isn't enough.

- Clone the repository and install with test dependencies:
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
*Remark*: as above, cloning is required if you want to actually run the tests.
- Clone and install:
    ```
    cd <path where you want to git clone>
    git clone https://github.com/marco-giunta/stringart.git
    cd stringart
    pip install .[ui,test]
    ```

#### Developer installation
To work on the code, clone the repo and install in editable mode with test and UI dependencies:
```
cd <path where you want to git clone>
git clone https://github.com/marco-giunta/stringart.git
cd stringart
pip install -e .[test,ui]
```