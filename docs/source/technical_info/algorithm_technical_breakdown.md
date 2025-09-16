# Behind *StringArt*: how does its algorithm work?

*Disclaimer*: the package's main algorithm was adapted from [kaspar98/StringArt](https://github.com/kaspar98/StringArt), but every bit of code here has been written from scratch with a different parametrization and extra caching features.

*Remark*: this document provide an overview of how the main algorithm works, as well as a high level reference for the stringart API (mostly the role of each module). Feel free to read only parts of this file; more details about each specific code bit can be found in the documentation.

## Introduction
### The algorithm in a nutshell
This package generates string art representations of images by simulating a thread stretched between nails placed along the border of a frame (either circular or rectangular). The algorithm approximates a target grayscale image by iteratively laying down virtual black strings on a white canvas, selecting each new string so that it maximally improves the resemblance to the original image. Said in another way: at each iteration, all possible lines starting from the current nail are drawn on top of the current canvas, and the one that causes the largest error decrease with respect to the target image is chosen.
This is an example of a *greedy algorithm*: we always choose the best possible improvement, meaning we don't account for the fact that, by choosing a worse line *now*, maybe *later on* we can get a much better cumulative improvement.
For this reason is no theoretical guarantee that the final recovered output is "optimal", even with a simple norm-based way to measure similarity between images; however, in practice by tweaking the parameters a bit using the tips given in the documentation it's usually possible to obtain a good enough result. It's possible that there exists a better way to choose the next nail, but either I am not aware/can't think of a smarter algorithm or an improved version of this algorithm would require much more effort (e.g. a ML reinforcement learning-based solver).

### Prerequisites
Let's now go more into detail of what's actually happening; before moving on some basic concepts about images are needed.
*Remark*: if you already know about pictures as matrices/arrays, antialiasing, caching and downscaling feel free to skip/skim through this section.

#### Images as matrices
- A grayscale picture is a matrix, i.e. a rectangle of numbers, each of which represents the brightness/intensity of the pixel whose positions in the photo corresponds to that particular matrix element. Each number goes from 0 (no brightness, i.e. black) to a maximum value (max brightness, i.e. white), with intermediate values representing shades of gray. Internally *StringArt* normalizes pixel values so that the max value (white) is 1 for simplicity. 
- A color photo simply contains three such matrices, corresponding to the red/green/blue (RGB) channels - meaning there are three matrices describing how much of each color goes into each pixel; when you open a photo these three matrices are combined to reproduce the correct image.
- If the input image is not already grayscale *StringArt* will convert it into grayscale i.e. a single matrix, with which we will compare our approximation.
- If the image is a PNG file and contains transparent portion, that information is encoded as a fourth channel (matrix), where each number represents the transparency of the pixel in the same position as the matrix element. In this case *StringArt* will use this information to replace the transparent portions of the image with a fixed background color (see docs).
- After the initial image has been preprocessed, *StringArt* will create a new matrix, initially containing all ones (i.e. an empty white image), which is called "canvas" in both the code and the docs, as this is the image on top of which we will draw black lines. The preprocessing algorithm then computes the positions of "nails", i.e. of allowed line vertices, which can be arranged on a rectangular layout (trivially laying on the edge of the canvas) or a circular arrangement laying inside the canvas (in which case the input image will be square cropped in the center to ensure we obtain the largest possible circle that can be inscribed inside the input image).

#### Antialiasing
Images are stored as rectangular grids of pixels, so they are inherently discrete. This creates a challenge: what if we want to draw a line that doesn’t align neatly with the pixel grid? Horizontal and vertical lines are straightforward, but diagonal or curved lines can look jagged or "stair-stepped."

To address this, we use a technique called antialiasing (AA). Antialiasing reduces these jagged "aliasing" artifacts by adjusting pixel intensities along the line’s edges, creating the visual impression of smooth, continuous lines.

In this project, line drawing is handled by [`scikit-image.draw.line_aa`](https://scikit-image.org/docs/0.25.x/api/skimage.draw.html#skimage.draw.line_aa), which calculates exactly which pixels to shade - and by how much - to produce the illusion of clean lines at any angle.

(This is enough for our purposes; feel free to look up AA online for more information.)

#### Internal downscaling
If we naively create a canvas with the same size as the original image the computation can be quite slow, especially if we're dealing with a very high resolution image. For this reason images are *downscaled* first, i.e. compressed to a lower resolution - thus ensuring the canvas is small enough to be drawn on easily. If the downscaling is too aggressive the visual quality of the result may be negatively impacted, but by using the tips given in the docs it's not difficult to find a good compromise between performance and visual quality.
*Remark*: After the computation is finished and we obtain the order of nails to connect with the antialiased lines, we can redraw the output at the original higher resolution of the input (see {class}`stringart.image_io.from_string_idx_order_to_image_array`), meaning that downscaling is only applied internally to speed the process up; by setting the parameter values correctly there will be no way to tell visually that the intermediate representations of the outputs were at a lower resolution.

#### Caching of possible lines
The number of nails along the chosen layout is fixed at the beginning by specifying the `num_nails` parameter. Given that the only allowed lines to be drawn on the canvas are those that start from a nail and end in another, there is a finite number of possible lines that the algorithm will ever consider drawing.
This means that a trick to speed up the computation is to precompute this finite set of allowed line; then we no longer have to use antialiasing to get them, we simply have to look up the needed line from a database.
This is exactly what happens with `precache_lines=True` (i.e. the default setting); another option is to use `cache_lines=True` and `precache_lines=False`, which means that lines are not precomputed but after the first time they are computed on the fly they are also saved in that database and looked up later if needed.

There is technically a catch: the number of lines (i.e. nail pairs) you can make increases *factorially* with `num_nails` (to be precise it's the binomial coefficient $\binom{N}{2}$). This means that if $n_t$ is too large the program will crash due to not enough memory, in which case it would be best to disable caching (i.e. to not save lines and recompute them every time). However, as long as $n_t$ is between ~100 and ~1000 there will be no problem and (pre)caching will indeed significantly speed up computation. With $n_t$ much larger than ~1000 the canvas will potentially become too crowded, impacting visual quality of the result; this means that in practice for the reasonable/recommended parameter ranges there is basically no reason to ever disable (pre)caching in practice.

## High level description, i.e. the core idea
- We start with a white canvas (all pixel values set to 1).
- Nails are placed on the border of the canvas in either:
- Circular layout: evenly spaced around a circle, or
- Rectangular layout: distributed along the edges of a rectangle.
- At each step, the algorithm draws a straight line (a simulated thread) between the current nail and another nail on the border.
- The line darkens pixels along its path by an amount determined by the string_strength. This approximates the cumulative effect of overlapping black thread.
- The choice of which nail to connect to next is determined by which candidate string produces the largest reduction in mean squared error (MSE) between the current canvas and the target image.

## Even more details: how the main functions work
### {class}`stringart` modules
{class}`stringart.create_stringart` ({class}`stringart.main.create_stringart`) calls functions from each module in order to do everything in a single call; in particular this is what happens.
- The provided input image is read using {class}`stringart.image_io` and preprocessed using {class}`stringart.transforms` if needed.
- A canvas (i.e. an empty white image array, on top of which we want to draw black lines) is computed using {class}`stringart.canvas`; the same module is also used to compute the nail positions depending on the choosen layout.
- {class}`stringart.skip` is used to decide which pairs of nails to ignore during the algorithm to speed up the computation (see docs or below).
- Finally, the main computation starts: by using {class}`stringart.pathfinding` or {class}`stringart.pathfinding_precache` the optimal nail-to-nail path is found and returned - after which the output can be saved using {class}`stringart.image_io`. Notice that these two modules do the same thing, they just differ in whether lines are computed during loop iterations (and then potentially saved in the soft cache) or whether they are all precomputed before the main loop and saved in the hard precache.
- The remaining modules are used for optional self-explanatory features ({class}`stringart.cli`, {class}`stringart.ui.app`, etc.); the only thing we actually need to explain in detail here is how the pathfinding module decides the sequence of nails to be connected.

### Comparing images
Let's say that at time $t$ we have a canvas containing a certain number of lines drawn in earlier iterations, and that we are currently at the nail with index $n_t$. Which nail should we choose to connect to nail $n_t$ in order to obtain the $t+1$ line?
The idea is that we want to compute a *distance* between the preprocessed input image and the current state of the canvas; the best sequence of nails is the one that minimizes the distance between input and output images, i.e. the one that maximizes similarity between them. In *StringArt* this distance computation is achieved by using the $L_2$/MSE (mean squared error) metric:

$$
d(T, C) = \sum_{i}\sum_{j} |T_{ij} - C_{ij}|^2
$$

where $T$ is the target matrix (the preprocessed input image) and $C$ is the canvas matrix (the current state of the output image).
Intuitively: we compare each pixel between the two images, compute the squared difference, then sum over all pixel locations $(i, j)$.
Given that at time $t$ we are at location $n_t$ we compute the $N_{\text{nails}}-1$ possible lines starting from $n_t$; the candidate that causes the greatest decrease in $d(T, C)$ is chosen as the $t+1$ line - and so on until either we reach the maximum number of allowed iterations or $d(T, C)$ stop significantly decreasing (see patience description in the docs).
This is why this is a *greedy algorithm*: we *always* chooses the line that causes the fastest decrease in $d(T, C)$ given only the current iteration, which means we ignore the possible sequences that give a smaller improvement now but a much better distance decrease down the line.
In one line: the $t+1$ nail has index

$$
n_{t+1} = \operatorname{argmin}_n D_{t+1}(n)
$$

where

$$
D_{t+1}(n) = d(T, C_{t+1}(n)) - d(T, C_t) = \sum_{i, j} |T_{ij} - C_{ij}^{t+1}(n)|^2 - \sum_{i, j} |T_{ij} - C_{ij}^t|^2
$$

where $C_{t+1}(n)$ is the new state of the canvas assuming we draw a line going from nail $n_t$ to the candidate $n$.
Notice that in the above for each value of $i$ and $j$ we are computing only the $L_2$ *variation*

$$
\Delta_{ij} = |T_{ij} - C_{ij}^{t+1}(n)|^2 - |T_{ij} - C_{ij}^t|^2
$$

But when drawing a line only certain pixels will be modified, meaning values of $i$ and $j$ away from those will not be modified. In practice this means that most of these differences will actually trivially be equal to zero, and therefore it's a waste computing them in the first place. For this reason in the pathfinding modules the above differences are actually computed only on the pixel values that were modified by that particular candidate line, i.e. the image arrays are first evaluated on the row/column coordinates of the candidate line, then the differences are actually computed. This trick is helpful to speed up performance, and can be applied thanks to the linearity of the sum of the squared differences (meaning it would also work with any other $L_p$ norm).


The values of $d(T, C)$ as a function of iteration time $t$ can also be saved as an optional output for visualization purposes (see documentation). Notice that in this case the normalized MSE is actually returned, i.e.

$$
d(T, C) = \frac{1}{N_p} \sum_i\sum_j |T_{ij}-C_{ij}|^2
$$

where $N_p=W\times H$ is the number of pixels, obtained by computing the width (number of columns) and height (number of rows) of the *downscaled* input image (because it's the one actually used as comparison for the intermediate states of the canvas).

### Iterative optimization-based pathfinding algorithm
In practice, the previous conceptual description happens as follows inside the pathfinding module(s).
1. *Selecting the Next Nail*
    The function {class}`get_next_nail_position` handles the selection:
    - It evaluates all candidate nails (excluding invalid ones):
        - Cannot connect a nail to itself.
        - For circular layouts, only nails whose angular distance from the current nail exceeds `min_angle_diff` are allowed (to prevent lines that barely cross the canvas and therefore barely affect the image).
    For each valid candidate:
        1. Compute the antialiased line between the current nail and the candidate nail.
        2. Estimate how much drawing this line would reduce the squared error relative to the target image.
        3. Keep track of the best improvement.
    - The nail that maximizes the error reduction is chosen as the next nail, and the canvas is updated accordingly.

2. *Iterative Path Construction*
    The function {class}`get_optimal_string_path` manages the entire process:
    - Start from a fixed or random initial nail (currently index 0).
    - Iteratively:
        1. Call get_next_nail_position to choose the next nail.
        2. Update the canvas with the new line.
        3. Record the new MSE and the chosen nail index.
    - The loop continues for up to max_num_iter iterations or until early stopping:
        - If improvement is smaller than epsilon for patience consecutive iterations, the algorithm halts.

### API parameters
{class}`get_optimal_string_path` requires the following arguments:

- `canvas`: Initial white canvas, normalized to `[0, 1]`.
- `nail_positions`: Array of `(row, col)` coordinates for each nail.
- `original_img`: Target grayscale image, normalized to `[0, 1]`.
- `string_strength`: Amount by which a single line darkens pixels along its path.
- `nail_layout`: Either `"circle"` or `"rectangle"`.
- `nail_angles`: (Circular layout only) Angles of nails in radians.
- `min_angle_diff`: (Circular layout only) Minimum angular separation between consecutive strings.
- `cache_lines`: Whether to cache computed line rasterizations for efficiency.
- `max_num_iter`: Maximum number of strings to lay down.
- `patience` / `epsilon`: Early stopping criteria.

Notice that if this function is not called directly, but instead internally via {class}`stringart.create_stringart` or equivalently {class}`stringart.main.create_stringart`, then there is no need to manually load/transform the input image or define the canvas or the nail positions/angles array; `create_stringart` will make the necessary calls to {class}`stringart.image_io`, {class}`stringart.transforms` and {class}`stringart.canvas`.

### Outputs
The {class}`get_optimal_string_path`/{class}`create_stringart` functions return:
- `string_idx_order`: Sequence of nail indices visited during the computation, i.e. the order in which the thread should be wound to reproduce the final image.
- `canvas`: Final canvas image after all iterations.
- `distance_vec`: Array of MSE values at each iteration, useful for plotting convergence.

## Summary
This approach is a *greedy optimization algorithm*:
- Each step chooses the best possible line based on local error reduction.
- Over many iterations, the thread path gradually builds up an image-like approximation.
- By adjusting the number of nails, string strength, and iteration count, you can balance performance with visual quality in the final artwork.

## Bonus: why the $L_2$ norm?
There are many ways to compare two images; the $L_2$ norm defined above is probably the easiest and one of the most used, but it's actually kind of naive. A better approach would be to use a machine learning based metric, as that would be able to more strongly penalize parts of the image that a human would rate as more wrong; vice versa, it would ignore pixel differences that a human wouldn't really notice. The problem is that obtaining such a specialized distance would at the very least require fine tuning a preexisting model, and for simplicity here we use the lazy approach of a fixed, easy to compute, easy to interpret distance metric. In practice it works well enough - also thanks to the other approximations introduced (grayscaling, downscaling, etc.), which reduce the original image's information content anyway.

Another advantage of using the $L_2$ norm is that can we exploit the linear sum of squared differences to simplify array evaluations, obtaining a decent performance improvement (see above).