import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--include-dir", action='store_true')

argv = parser.parse_args()
if argv.include_dir:
    print(os.path.join(os.path.dirname(__file__), 'include'))