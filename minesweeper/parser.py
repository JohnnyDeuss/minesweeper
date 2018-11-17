""" The argument parser, defining the commandline arguments that can be passed.
    The parser simply sets up and parses the args with `argparse.ArgumentParser`.
"""
from argparse import ArgumentParser


def parse_args():
    """ Parse `sys.argv`. """
    parser = ArgumentParser(description='The classical Minesweeper game.')
    parser.add_argument('--debug', action='store_true', dest='debug_mode', help='Add a debug menu to export the state '
                                                                                'and ground truth of the game.')
    # Allow the setting of the difficulty
    group = parser.add_mutually_exclusive_group(required=False)
    group.set_defaults(difficulty='expert')
    group.add_argument('--beginner', action='store_const', const='beginner', dest='difficulty')
    group.add_argument('--intermediate', action='store_const', const='intermediate', dest='difficulty')
    group.add_argument('--expert', action='store_const', const='expert', dest='difficulty', default='expert')
    group.add_argument('--custom', nargs=3, dest='dims', metavar=('width', 'height', 'num_mines'))

    args = parser.parse_args()
    # Shift arguments around a bit to be more easily usable.
    if args.dims is not None:
        args.difficulty = 'custom'
        args.width, args.height, args.num_mines = args.dims
    del args.dims
    return args
