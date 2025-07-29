# monpackage/cli.py

import argparse
from .core import add

def main():
    parser = argparse.ArgumentParser(description="Additionne deux nombres.")
    parser.add_argument("a", type=float, help="Premier nombre")
    parser.add_argument("b", type=float, help="Deuxième nombre")
    args = parser.parse_args()

    result = add(args.a, args.b)
    print(f"Résultat : {result}")
