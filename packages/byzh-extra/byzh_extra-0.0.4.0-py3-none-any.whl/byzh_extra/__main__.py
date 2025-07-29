import argparse

def py2ipynb():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", '-n', help="py文件")
    args = parser.parse_args()

    from .Bconvert import b_py2ipynb
    b_py2ipynb(args.name)

def ipynb2py():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", '-n', help="ipynb文件")
    args = parser.parse_args()

    from .Bconvert import b_ipynb2py
    b_ipynb2py(args.name)

