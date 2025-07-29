import argparse

parser = argparse.ArgumentParser(
    prog="kmeruniq",
    description="Build genomic kmer-based datastructure with unique constraint",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.set_defaults(func=lambda e: e)
subparsers = parser.add_subparsers(required=True)
