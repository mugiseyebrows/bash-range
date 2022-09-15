import sys
from . import expand_args

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0 and args[0] in ['-v', '--verbose']:
        debug = True
        args = args[1:]
    else:
        debug = False
    if debug:
        print("args: ", " ".join(args))
    print(" ".join(expand_args(args, debug)))