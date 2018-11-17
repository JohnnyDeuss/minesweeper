""" The argument parser, defining the commandline arguments that can be passed.
    The parser simply sets up and parses the args with `argparse.ArgumentParser`.
"""
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser(description='The classical Minesweeper game.')
    parser.add_argument('--debug', action='store_true', help='Add a debug menu to export the state and ground truth '
                                                             'of the game.')
    return parser.parse_args()
