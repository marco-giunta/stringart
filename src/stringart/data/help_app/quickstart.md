Welcome to the StringArt webapp! This tool lets you approximate an input image using a single continuous string looped around nails placed on the border of a canvas.  
The app provides a simple interface to upload an image, choose parameters, and visualize the resulting string art.

---

### Quick guide

1. **Choose an input image**  
   - Upload your own image (recommended image: square crop & grayscale/simple contrast, see tips for more details);
   - Otherwise select one of the built-in demo images.

2. **Set the base parameters**  
   - Number of nails, rescale factor, layout, etc. (see below).  
   - For first trials, keep defaults and just adjust nails to ~200–300.

3. **Click *Generate***  
   - The algorithm starts and will render the stringart in the **Output** tab.  
   - Depending on the parameters, this can take a few seconds up to several minutes.
   - *Generate button bug*: please note that the **Generate** button is currently broken; to start image generation please click on the **Output** tab.

4. **Inspect the output**  
   - The final stringart is shown as a grayscale image.  
   - You can save results by using the CLI version with `--output`.

---

### Known bugs

- The **Generate** button is currently broken; to start image generation please click on the **Output** tab.  
- Being on the **Output** tab and modifying one parameter is enough to trigger the computation to start again immediately. Therefore if you want to modify multiple parameters, please move to another tab first, then go back to the output tab when you're ready.
- The loading/progress bar is not shown inside the UI yet. To monitor progress, check the terminal where you started the Shiny app.  
- Switching themes *during computation* may cause display glitches (text may become invisible). Switching back or refreshing the page usually fixes it (but then you may need to restart the computation).
- Download functionality is broken/missing; to save the image, the string index order or the distance vector please use the CLI. Alternatively: if you simply want to save the output image, try right clicking it and using your browser's "Download/Save As..." (possibly after opening it in a new tab to better visualize it). Notice that in this case you are not downloading the direct output computed by `stringart` (i.e. the one you'd obtain by switching to the CLI or the API), but the image rendered by shiny, meaning the downloaded picture may have some extra empty white space and/or a different resolution (nothing a bit of photo editing can't solve if you're determined enough).

---