import numpy as np
import time
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from pathlib import Path
from importlib.util import find_spec
from stringart.pathfinding import get_optimal_string_path
from stringart.pathfinding_precache import get_optimal_string_path_precache, precache_lines
from stringart.skip import get_should_skip_function
from stringart.canvas import create_canvas_and_nail_positions
from stringart.image_io import open_grayscale_crop_fixbg_img
from stringart.demo import get_demo_image_path
from stringart.transforms import downscale

# use downscaled demo einstein image
def make_test_case(num_nails, downscale_factor):
    img = downscale(open_grayscale_crop_fixbg_img(get_demo_image_path('einstein.jpg'), (50, 50, 50), "circle"), downscale_factor)
    return create_canvas_and_nail_positions(img.shape, "circle", num_nails), img

# in practice one would use a downscale factor between 0.2 and 0.5 and a max_iter of at least a few thousands with einstein.jpg;
# here we are cutting these parameter values down to obtain a faster (albeit slightly less accurate) benchmark
DOWNSCALE_FACTOR = 0.1
MAX_ITER = 3000
STRING_STRENGTH = 0.1
nails_list = [50, 100, 250, 500, 750, 900]
# IMPORTANT REMARK: run with these parameters only with 32+ GB of RAM and other programs closed! 
# Otherwise it's best to decrease the number of nails, as the cache size may crash the program

def benchmark_caching(num_nails, downscale_factor = DOWNSCALE_FACTOR, max_iter = MAX_ITER, string_strength = STRING_STRENGTH):
    (canvas, nail_positions, angles), original_img = make_test_case(num_nails, downscale_factor=downscale_factor)
    results = {}

    # --- No cache ---
    print("No cache run:")
    start = time.time()
    _ = get_optimal_string_path(canvas.copy(), nail_positions,
                                original_img, string_strength,
                                max_num_iter=max_iter,
                                nail_layout="circle",
                                nail_angles=angles,
                                cache_lines=False)  # no caching at all
    runtime = time.time() - start
    results["no_cache"] = {"precaching": 0.0, "loop": runtime, "total": runtime}

    # --- Soft cache ---
    print("Soft cache run:")
    start = time.time()
    _ = get_optimal_string_path(canvas.copy(), nail_positions,
                                original_img, string_strength,
                                max_num_iter=max_iter,
                                nail_layout="circle",
                                nail_angles=angles,
                                cache_lines=True)  # soft caching
    runtime = time.time() - start
    results["soft_cache"] = {"precaching": 0.0, "loop": runtime, "total": runtime}

    # --- Hard cache ---
    print("Hard cache run:")
    print("Precache:")
    # 1. Explicit precaching
    start = time.time()
    precomputed_lines = precache_lines(nail_positions, 0.1, original_img.shape, get_should_skip_function("circle", angles))
    precache_time = time.time() - start

    print("Actual cache run (after precache):")
    # 2. Main loop with precomputed lines NOT passed in
    start = time.time()
    _ = get_optimal_string_path_precache(canvas.copy(), nail_positions,
                                         original_img, string_strength,
                                         max_num_iter=max_iter,
                                         nail_layout="circle",
                                         nail_angles=angles,
                                         line_cache_dict=precomputed_lines)
    loop_time = time.time() - start

    results["hard_cache"] = {
        "precaching": precache_time,
        "loop": loop_time,
        "total": loop_time + precache_time
    }

    return results

p = Path(__file__).absolute().parent / 'benchmarks.pkl'

try:
    with open(p, 'rb') as f:
        benchmarks = pickle.load(f) # skip the computation if already done in the past
    print(f'Benchmark found at {p}')
except:
    benchmarks = {}
    for N in nails_list:
        print(f"--------------- Benchmarking {N=} ---------------")
        benchmarks[N] = benchmark_caching(N)
        print("\n")
    
    with open(p, 'wb') as f:
        pickle.dump(benchmarks, f)

rows = []
for N in nails_list:
    b = benchmarks[N]
    rows.append({
        "N": N,
        "no_cache_total": b["no_cache"]["total"],
        "soft_cache_total": b["soft_cache"]["total"],
        "hard_cache_precaching": b["hard_cache"]["precaching"],
        "hard_cache_loop": b["hard_cache"]["loop"],
        "hard_cache_total": b["hard_cache"]["total"],
    })

df = pd.DataFrame(rows)

df = df.round(4)
p = Path(__file__).absolute().parent / 'benchmark_table.csv'

if not p.exists():
    df.to_csv(p)
    print(f'Saved {p}.')

if find_spec("tabulate") is not None:
    print(df.to_markdown())
    p = Path(__file__).absolute().parent / 'benchmark_table.md'
    with open(p, 'w') as f:
        f.write(df.to_markdown())
else:
    print(df)


labels = ["no_cache", "soft_cache", "hard_cache"]
x = np.arange(len(nails_list))  # positions for groups
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))

# --- No cache ---
no_vals = [benchmarks[N]["no_cache"]["total"] for N in nails_list]
ax.bar(x - width, no_vals, width, label="No cache")

# --- Soft cache ---
soft_vals = [benchmarks[N]["soft_cache"]["total"] for N in nails_list]
ax.bar(x, soft_vals, width, label="Soft cache")

# --- Hard cache (stacked) ---
hard_precache = [benchmarks[N]["hard_cache"]["precaching"] for N in nails_list]
hard_loop = [benchmarks[N]["hard_cache"]["loop"] for N in nails_list]

ax.bar(x + width, hard_precache, width, label="Hard cache (precaching)", color="lightgray")
ax.bar(x + width, hard_loop, width, bottom=hard_precache,
       label="Hard cache (main loop)", color="black")

# --- Formatting ---
ax.set_xlabel("Number of nails (N)")
ax.set_ylabel("Runtime (seconds)")
ax.set_title("Caching strategies runtime comparison")
ax.set_xticks(x)
ax.set_xticklabels([str(N) for N in nails_list])
ax.legend()
ax.grid(True, axis="y", linestyle="--", alpha=0.6)

p = Path(__file__).absolute().parent / 'benchmark_plot.png'

if not p.exists():
    plt.savefig(p)
    print(f'Saved {p}.')

plt.show()