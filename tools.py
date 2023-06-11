import sys

def log(string : str) -> None:
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()