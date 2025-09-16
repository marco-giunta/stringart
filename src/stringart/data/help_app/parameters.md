### Parameters description
There are two types of parameters you can set in *StringArt*.
- *base parameters*: parameters that you (may) need to tweak yourself, even when default values are provided - so please read this section carefully!
- *advanced parameters*: parameters that you can ignore, as they control technical parts of the algorithm that you probably have no reason to interact with. These parameters are left here mostly for debugging reason, but feel free to read about them and modify their values if you want more control over what the algorithm does.

(For each webapp parameter you can find in parentheses the name of the corresponding CLI variable)

#### Base parameters

- **Input image (`--input`)**
  Upload a file (`.png`, `.jpg`, `.jpeg`, `.pdf`) or select a demo image.
  
  The chosen image will then be preprocessed as follows:
  - The image will be converted to grayscale if not already black/white.
  - If the circular nail layout is selected (see below), the image will be square cropped in the center, meaning that landscape pictures will be trimmed left and right and portrait pictures will be trimmed up and down. If the center portion of the original image is *not* what you are interested in computing, please pre-crop your image, leaving only the elements you care about.
  - If the provided image is a `.png` file and it contains a transparent background because e.g. you used an AI app to remove unwanted background elements (as recommended, see tips tab), this transparent background will be replaced with the flat color specified by the `background-color` parameter (see below).

- **Number of nails (`--nails`)**  
  Sets how many nails are placed around the canvas border.  

  - More nails → higher resolution but slower computation.  
  - Typical values: 150–400 (i.e. order of hundreds).  
  - For circular layouts, nails are evenly spaced along the circle.

  *Intuitively*: with a larger number of available nails, the algorithm has a finer control over space and can reach tiny regions with less constraints.

  For circular layouts if circular artifacts appear (i.e. rings in the inner parts of the image) try increasing the number of nails by ~50-100 and see what happens.

- **Downscale factor (`--downscale`)**  
  Controls how much the input image is downscaled before processing.  
  
  - Lower values (e.g. 0.5 → halve the resolution) → faster, coarser results.  
  - Higher values (e.g. 1.0 → keep the original resolution) → slower, more detailed results.

  A good tradeoff (an image with decent quality that is computed in 30 seconds to 2 minutes) can usually be achieved by choosing a `downscale` factor that causes your original image to go down to ~300-700 px per side. For example: if your input image is full HD i.e. ~1000-2000 px per side, you may want to choose `downscale` between 0.25 and 0.5, so that your downscaled image is ~500x500 px.

  Please notice that, while this affects the result as it changes the internal resolution during computation, the output image will be upscaled back to the original resolution; therefore don't worry about obtaining a tiny output image in the end! Feel free to tweak this parameter to control the performance/visual quality tradeoff.

- **Layout (`--layout`)**  
  Defines nail arrangement:  

  - `circle` (default): nails evenly distributed on a circular border. This will cause the preprocessing algorithm to crop a square at the center of the image, then place nails in the largest circle that fits that square.
  - `rectangle`: nails placed along the edges of a rectangle. This will cause the preprocessing algorithm to skip cropping, i.e. the edge of the original image will be used as the canvas' boundary along which to place nails.

  The circular layout is strongly recommended, as using a rectangular layout will heavily constrain the freedom the solver must populate space with lines.

- **String strength (`--strength`)**  
  Scaling factor for how strongly each string stroke contributes to the image. 

  - Default: `0.1`.  
  - Higher values → darker strings.  
  - Lower values → lighter effect.

  *Intuitively*: think of this parameter as the thickness of our virtual black string: a thicker string produces a darker, more filled-in image. If the default string strength value causes the image to appear "too white" or "too empty" try slightly increasing this parameter (e.g. from `0.1` to `0.2`). Similarly if the image appears "too dark" or "too filled" lower the parameter (typically by multiples of `0.1`).

- **Max iterations (`--maxiter`)**  
  Maximum number of string placements.  

  - Higher values → potentially more accurate image, but longer runtime.  
  - Default: `5000`.

  The algorithm needs to pass the string enough a large enough number of nails in order to accurately reproduce the details of the original image, therefore this value needs to be large enough - typically on the order of thousands, i.e. experiment with values ~5000-8000, etc.

  Please notice that *StringArt* is equipped with an early stopping feature (see `patience` and `epsilon` in the *Advanced parameters* section), meaning that if the image doesn't improve enough for a long enough time the algorithm will stop even if the maximum number of string placements has not been reached, in which case a message will be displayed on top of the loading bar.
  This typically happens when there are hard constraints to how accurately the algorithm is able to reconstruct the input image, which may be caused e.g. by a too small number of nails or by an excessively aggressive downscaling factor. Therefore if the algorithm stops early but you are not satisfied with output quality, try increasing those parameter values (but then expect a longer computation time).

- **Background color (`--background-color`)**  
  RGB tuple (with each value in the `[0-255]` range) used if the input image has transparency.  
  - Default: `(50, 50, 50)` (dark gray).

  If the provided image is a `.png` file and it contains a transparent background because e.g. you used an AI app to remove unwanted background elements (as recommended, see tips tab), this transparent background will be replaced with the flat color specified by the `background-color` parameter.
  It's recommended to use darker tones (but not too dark/too close to black), as that will give the algorithm enough freedom to cross this now empty region as much as needed (see tips section). If the chosen color is too dark the algorithm may be forced to focus too much on filling in this space rather than reproducing the original image, so play around with this color if needed.

- **Minimum angle difference (`--min-angle-diff`)**  
  Restricts the angular difference between consecutive nails (circular layout only).  
  - Prevents overlapping/near-parallel lines.  
  - Default: `π/8` radians, i.e. 22.5 degrees.

  When using the circular layout, if a line connects two neighbouring points then that line will barely affect the canvas, as it will barely detach itself from the edge. Lines that strongly affect the current state of the canvas are those that cross it in the middle and cover a large distance; in order to speed up computation, and consistently with the greedy nature of the algorithm, points that are too close (i.e. that barely change the current score) will be ignored. The `min_angle_diff` parameter controls how close two points have to be in order for the pair they define to be ignored; set this parameter to zero to disable the skipping mechanism entirely.
  If in doubt, don't modify the default: this value provides a good compromise between not enough skips (which needlessly slows down the computation, as those short lines are basically guaranteed to never be chosen) and too many skips (which causes the algorithm to potentially miss out on the lines that give the best possible visual quality).

  Notice that if `layout=="rectangle"` points on the same rectangle side are always skipped (as that line wouldn't cross the canvas at all, thus never modifying the current canvas state); similarly pairs corresponding to the same point are always ignored, as they don't define valid lines.

---

#### Advanced parameters
- **Precache / Cache options (`--no-cache`, `--no-precache`)**  
  Control whether string line paths are cached for speed.  
  - Leave caching **enabled** unless debugging.

  The number of nails if fixed, meaning there's only a finite number of possible lines that can ever be drawn on the canvas by connecting one of the $\binom{N}{2}$ possible pairs. By precomputing the coordinates and pixel values of all these lines, the algorithm can focus on just choosing the best one at any given iteration, without needing to recompute a line that's already potentially been used multiple times already. For this reason `stringart` by default caches lines; by default all possible lines are precomputed before starting the main loop, but there is also a soft caching strategy available where lines are saved only after the first time they are needed (i.e. no initial overhead, but also unreliable ETA and no clear separation between operations). 
  For typical values of `num_nails` precaching offers the fastest computation time, so it's recommended not to turn it off. The only potential downside is that, since the number of possible pairs (hence lines) scales factorially with $N$, if $N$ is too large precaching may fail due to not enough memory, with the no cache strategy technically the only working option. However this does not happen for reasonable values of `num_nails` (typically between 100 and 700); furthermore using too large values of $N$ will significantly slow down algorithm performance anyway, so it's not recommended to use values of $N$ that would require turning caching off. Still: if you want to use $N$ larger than ~800 you may need to disable precaching and possibly caching (unless you have at least 32 GBs of RAM available).

- **Patience (`--patience`) and epsilon (`--epsilon`)**  
  Control early stopping:  
  - If the improvement between iterations is less than `epsilon` for `patience` steps, the algorithm stops early.  
  - Defaults: `20` and `1e-6`.

  During iteration $t$ the algorithm chooses the line that causes the largest score improvement based on the score at time $t-1$. If the best possible improvement is smaller than `epsilon` the algorithm starts counting; if at some point the new best improvement is again larger than `epsilon` the "patience counter" is reset. If instead the counter reaches the `patience` value, the algorithm stops early, i.e. even if the maximum number of iterations has not yet been reached. 
  If `epsilon` is too small then the patience/early stopping mechanism is essentially disabled; if instead it's too large the algorithm may never reach a "complete" canvas state, i.e. a "finished" approximation of the input image. Similarly the `patience` parameter allows the algorithm to avoid a hard stop as soon as the best improvement is not good enough, protecting it from stopping on an unlucky iteration even if better improvements are actually available further down the line.

  It's recommended to ignore these parameters, as they are left accessible mostly for debug purposes. By choosing smartly the other more important parameters (`downscale_factor`, `num_nails`, `max_num_iter`, etc.) the patience mechanism won't activate or activate too early anyway.
---