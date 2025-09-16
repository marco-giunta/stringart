from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from numpy import pi, savetxt
from .main import create_stringart
from .image_io import open_grayscale_crop_fixbg_img, from_string_idx_order_to_image_array, save_stringart, resolve_output_path
from matplotlib.pyplot import imshow, show

def stringart_cli(argv = None):
    parser = ArgumentParser(
        description = "stringart CLI: approximate images using one long string looped around nails on a canvas from the comfort of your terminal",
        formatter_class = ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-i', '--input', type = str, help = 'input image path')

    parser.add_argument('-o', '--output', type = str, help = 'output image path; this can be just the folder path (in which case the default name "output.png" will be used) or can also include a custom file name. Supported extensions: [".png", ".jpg", ".jpeg", ".pdf"]')
    parser.add_argument('-so', '--string_order', type = str, help = 'path where to save the computed string nail index order; this can be just the folder path (in which case the default name "string_idx_order.txt" will be used) or can also include a custom file name. Supported extensions: ".txt"')
    parser.add_argument('-ds', '--distance', type = str, help = 'path where to save the computed distance between working and target image, as a function of time; this can be just the folder path (in which case the default name "distance.txt" will be used) or can also include a custom file name. Supported extensions: ".txt"')

    parser.add_argument('-n', '--nails', type = int, help = 'number of nails to use')
    parser.add_argument('-d', '--downscale', type = float, help = 'downscale factor used to compress the image')
    parser.add_argument('-s', '--strength', type = float, help = 'string strength factor', default = 0.1)
    parser.add_argument('-ni', '--maxiter', type = int, help = 'max number of iterations', default = 5000)
    parser.add_argument('-l', '--layout', type = str, help = 'nail layour ("circle" or "rectangle")', default = 'circle')
    parser.add_argument('-nc', '--no-cache', help = 'disable caching of lines (on by default)', action = 'store_true')
    parser.add_argument('-npc', '--no-precache', help = 'disable precaching of lines (on by default)', action = 'store_true')
    parser.add_argument('-mad', '--min-angle-diff', type = float, help = 'min angle difference to use if layout == "circle" in radians (default pi/8)', default = pi/8)
    parser.add_argument('-bc', '--background-color', type = int, nargs = 3, metavar = ('R', 'G', 'B'), help = "sequence of 3 int RGB values in [0-255] to use to replace a PNG's transparent background if present (default (50, 50, 50) i.e. dark gray)", default = (50, 50, 50))
    parser.add_argument('-p', '--patience', type = int, help = 'patience counter (max num. of iterations with no improvement > eps after which the program stops early)', default = 20)
    parser.add_argument('-e', '--epsilon', type = float, help = 'absolute improvement needed between iterations to avoid increasing early stopping/patience counter', default = 1e-6)

    args = parser.parse_args(argv)

    string_idx_order, canvas, distance_vec = create_stringart(
        img_path = args.input,
        num_nails = args.nails,
        downscale_factor = args.downscale,
        string_strength = args.strength,
        max_num_iter = args.maxiter,
        nail_layout = args.layout,
        cache_lines = not args.no_cache,
        precache_lines = not args.no_precache,
        min_angle_diff = args.min_angle_diff,
        background_color = args.background_color,
        patience = args.patience,
        epsilon = args.epsilon
    )

    # print('string index order:\n', [int(x) for x in string_idx_order])

    img = open_grayscale_crop_fixbg_img(args.input, args.background_color, args.layout)

    canvas = from_string_idx_order_to_image_array(
        string_idx_order = string_idx_order,
        shape = img.shape,
        nail_layout = args.layout,
        num_nails = args.nails,
        string_strength = args.strength/args.downscale
    )

    if args.output is not None:
        out_path = resolve_output_path(
            user_path=args.output,
            default_name="output.png",
            allowed_exts=[".png", ".jpg", ".jpeg", ".pdf"]
        )
        save_stringart(canvas, out_path)
        print(f'Saved output image to {out_path}.')

    if args.string_order is not None:
        out_path = resolve_output_path(
            user_path=args.string_order,
            default_name='string_idx_order.txt',
            allowed_exts='.txt'
        )
        savetxt(out_path, string_idx_order, fmt = '%d')
        print(f'Saved string index order to {out_path}.')

    if args.distance is not None:
        user_path = resolve_output_path(
            user_path=args.distance,
            default_name='distance.txt',
            allowed_exts='.txt'
        )
        savetxt(user_path, distance_vec, fmt = '%.7f')
        print(f'Saved distance vector to {out_path}.')
    
    imshow(canvas, cmap='gray')
    show()


if __name__ == '__main__':
    stringart_cli()