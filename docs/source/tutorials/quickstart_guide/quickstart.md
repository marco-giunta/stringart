# Quickstart

## Python API (code-based)
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

## CLI (text-based)
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

## Shiny WebApp (UI-based)

### Starting the WebApp
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
- Click on that `http://127.0.0.1:xxxx` link (depending on your terminal app you may need to do something like CTRL+click) or copy/paste it into your browser of choice.

- Once you're done, close the browser tab, go back to the terminal and press CTRL+C.

### Using the WebApp
- To use the webapp upload your image (or use a demo one), tweak the parameter values using the sidebar menu, and view your output in the output tab.
- The webapp also has a "help" section you can read to learn every detail about how to set each parameter without needing to read the documentation or the rest of this readme; there are also some useful trick to ensure optimal visual accuracy in the result.
- This is the recommended option for non technical users, but please note that webapp support is still experimental; there are some known bugs (see the webapp's help section) and some functionality is missing, so using the API or the CLI may be unavoidable for some users.