# Advanced parameters
- **Precache / Cache options (`cache_lines`, `precache_lines`; `-nc, --no-cache`, `-npc, --no-precache` - opposite definitions)**  
  Control whether string line paths are cached for speed.  
  - Leave caching **enabled** unless debugging.

  The number of nails if fixed, meaning there's only a finite number of possible lines that can ever be drawn on the canvas by connecting one of the $\binom{N}{2}$ possible pairs. By precomputing the coordinates and pixel values of all these lines, the algorithm can focus on just choosing the best one at any given iteration, without needing to recompute a line that's already potentially been used multiple times already. For this reason `stringart` by default caches lines; by default all possible lines are precomputed before starting the main loop, but there is also a soft caching strategy available where lines are saved only after the first time they are needed (i.e. no initial overhead, but also unreliable ETA and no clear separation between operations). 
  For typical values of `num_nails` precaching offers the fastest computation time, so it's recommended not to turn it off. The only potential downside is that, since the number of possible pairs (hence lines) scales factorially with $N$, if $N$ is too large precaching may fail due to not enough memory, with the no cache strategy technically the only working option. However this does not happen for reasonable values of `num_nails` (typically between 100 and 500); furthermore using too large values of $N$ will significantly slow down algorithm performance anyway, so it's not recommended to use values of $N$ that would require turning caching off. Still: if you want to use $N$ larger than ~800 you may need to disable precaching and possibly caching (unless you have at least 32 GBs of RAM available).

- **Patience (`patience`; `-p`, `--patience`) and epsilon (`epsilon`; `-e`, `--epsilon`)**  
  Control early stopping:  
  - If the improvement between iterations is less than `epsilon` for `patience` steps, the algorithm stops early.  
  - Defaults: `20` and `1e-6`.

  During iteration $t$ the algorithm chooses the line that causes the largest score improvement based on the score at time $t-1$. If the best possible improvement is smaller than `epsilon` the algorithm starts counting; if at some point the new best improvement is again larger than `epsilon` the "patience counter" is reset. If instead the counter reaches the `patience` value, the algorithm stops early, i.e. even if the maximum number of iterations has not yet been reached. 
  If `epsilon` is too small then the patience/early stopping mechanism is essentially disabled; if instead it's too large the algorithm may never reach a "complete" canvas state, i.e. a "finished" approximation of the input image. Similarly the `patience` parameter allows the algorithm to avoid a hard stop as soon as the best improvement is not good enough, protecting it from stopping on an unlucky iteration even if better improvements are actually available further down the line.

  It's recommended to ignore these parameters, as they are left accessible mostly for debug purposes. By choosing smartly the other more important parameters (`downscale_factor`, `num_nails`, `max_num_iter`, etc.) the patience mechanism won't activate or activate too early anyway.
---