import argparse
import os, sys

class HiddenPrints:
    """
    A context in which all the prints get discarded
    """
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def build_argparser():
    """
    Builds a parser for command-line arguments
    :return: an argparser
    """
    parser = argparse.ArgumentParser(description='Waiter Bot')
    parser.add_argument('--dep_tree', action="store_true",
                        help='print dependencies tree of every heard sentence')

    return parser