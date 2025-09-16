from importlib.util import find_spec

if find_spec("shiny") is not None:
    from shiny import App, ui, Inputs, Outputs, Session, render, reactive
else:
    raise RuntimeError(
        "Shiny is not installed. To use the web UI, install the optional dependencies:\n"
        "    pip install stringart[ui]"
    )

from pathlib import Path
import tempfile
import matplotlib.pyplot as plt
from .main import create_stringart
from .image_io import (
    open_grayscale_crop_fixbg_img,
    from_string_idx_order_to_image_array,
    save_stringart
)
import importlib.resources as pkg_resources
from . import data
from .demo import list_demo_images, get_demo_image_path

# Load help text
def load_help_markdown(filename):
    help_path = pkg_resources.files(data) / "help_app" / filename
    return help_path.read_text(encoding="utf-8")


def run_stringart(img_path, layout, nails, downscale, strength,
                  maxiter, precache, cache, min_angle_diff,
                  background_color, patience, epsilon):
    img = open_grayscale_crop_fixbg_img(img_path, background_color=background_color, nail_layout=layout)

    string_idx_order, canvas, distance_vec = create_stringart(
        img_path=img_path,
        num_nails=nails,
        downscale_factor=downscale,
        string_strength=strength,
        max_num_iter=maxiter,
        nail_layout=layout,
        cache_lines=cache,
        precache_lines=precache,
        min_angle_diff=min_angle_diff,
        background_color=background_color,
        patience=patience,
        epsilon=epsilon,
    )

    canvas = from_string_idx_order_to_image_array(
        string_idx_order=string_idx_order,
        shape=img.shape,
        nail_layout=layout,
        num_nails=nails,
        string_strength=strength / downscale
    )

    return canvas

themes = ui.Theme.available_presets()

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h5("Please read the help section first!"),
        ui.input_select("theme", "Choose a theme", {t: t for t in themes}, selected="zephyr"),
        ui.input_file("input_file", "Upload an image...", accept=[".png", ".jpg", ".jpeg"]),
        ui.input_select(
            "demo_image",
            "...or choose a demo image",
            {img_fname: img_fname for img_fname in list_demo_images()},
            selected="einstein.jpg",
        ),
        ui.h3("Settings"),
        ui.input_radio_buttons("layout", "Layout", {"circle": "Circle (recommended)", "rectangle": "Rectangle"}),
        ui.input_numeric("nails", "Number of nails", 200, min=50, max=2000),
        ui.input_numeric("downscale", "downscale factor", 0.3, min=0.1, max=1.0, step=0.1),
        ui.input_numeric("strength", "String strength", 0.1, min=0.01, max=1.0, step=0.01),
        ui.input_numeric("maxiter", "Max iterations", 7000, min=100, max=50000),
        ui.h3("Advanced settings"),
        ui.input_checkbox("cache", "Cache lines", True),
        ui.input_checkbox("precache", "Precache lines", True),
        ui.input_numeric("min_angle_diff", "Min. angle diff. (rad)", 0.39, min=0.0, max=3.14, step=0.01),
        ui.input_numeric("patience", "Patience (# iterations)", 20, min=5, max=50, step=1),
        ui.input_numeric("epsilon", "epsilon", 1e-6, min=1e-8, max=1e-3),
        ui.input_numeric("bg_r", "R ch. transparent PNG bg", 50, min=0, max=255, step=1),
        ui.input_numeric("bg_g", "G ch. transparent PNG bg", 50, min=0, max=255, step=1),
        ui.input_numeric("bg_b", "B ch. transparent PNG bg", 50, min=0, max=255, step=1),
        
        ui.input_action_button("generate", "Generate"),
    ),
    ui.output_ui("tabs"),
    title="StringArt Web UI"
)

help_tab = ui.nav_panel(
    "Help",
    ui.navset_tab(
        ui.nav_panel("Quickstart", ui.markdown(load_help_markdown("quickstart.md"))),
        ui.nav_panel("Parameters", ui.markdown(load_help_markdown("parameters.md"))),
        ui.nav_panel("Tips", ui.markdown(load_help_markdown("tips.md"))),
    )
)

def server(input: Inputs, output: Outputs, session: Session):

    last_canvas = reactive.Value(None)

    @output
    @render.image
    def input_preview():
        if input.input_file():
            f = input.input_file()[0]
            return {"src": f["datapath"], "alt": f["name"], **dict(height="600px", width="auto")} # **dict(width="auto", height="100%") width="100%"
        else:
            demo_path = get_demo_image_path(input.demo_image())
            return {"src": str(demo_path), "alt": demo_path.name, **dict(height="600px", width="auto")} # **dict(width="auto", height="100%") width="100%" o 400px

    @output
    @render.plot
    def stringart_plot(width=600, height=600, res=150):# width/height in pixels, res = dpi
        input.generate()  # wait for button click

        # User upload takes priority, else demo image
        if input.input_file():
            img_path = Path(input.input_file()[0]["datapath"])
        else:
            img_path = get_demo_image_path(input.demo_image())

        canvas = run_stringart(
            img_path=img_path,
            layout=input.layout(),
            nails=input.nails(),
            downscale=input.downscale(),
            strength=input.strength(),
            maxiter=input.maxiter(),
            precache=input.precache(),
            cache=input.cache(),
            min_angle_diff=input.min_angle_diff(),
            background_color=(input.bg_r(), input.bg_g(), input.bg_b()),
            patience=input.patience(),
            epsilon=input.epsilon(),
        )

        last_canvas.set(canvas)

        fig, ax = plt.subplots() #plt.subplots(figsize=(8, 8), dpi=150)  # width=8", height=8", higher DPI causa un loop
        ax.imshow(canvas, cmap="gray")
        ax.axis("off")
        return fig
    
    @output
    @render.download(filename=lambda: "stringart.png")
    def download_canvas():
        def writer(path):
            canvas = last_canvas.get()
            if canvas is None:
                raise ValueError("No canvas computed yet!")

            fmt = input.download_format()

            if fmt == "pdf":
                # PDF requires a figure context
                fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
                ax.imshow(canvas, cmap="gray")
                ax.axis("off")
                fig.savefig(path, format="pdf", bbox_inches="tight")
                plt.close(fig)
            else:
                # For PNG and JPEG, write directly
                plt.imsave(path, canvas, cmap="gray", format=fmt)
        return writer

    @output
    @render.ui
    def tabs():
        return ui.page_fluid( # in server anziché fuori in modo che possa reagire con il tema assegnato nella parte di ui che lascio fuori
                ui.navset_tab(
                ui.nav_panel("Input", ui.output_image("input_preview")),
                ui.nav_panel(
                    "Output",
                    ui.output_plot("stringart_plot"),

                    ui.input_select(
                        "download_format",
                        "Image format",
                        choices=["png", "jpeg", "pdf"],
                        selected="png"
                    ),
                    ui.download_button("download_canvas", "Download result"),
                    ),
                help_tab,
                id="main_tabs",
            ),
            theme=ui.Theme(preset=input.theme())
        )

app = App(app_ui, server)

def stringart_app():
    app.run()

if __name__ == "__main__":
    stringart_app()