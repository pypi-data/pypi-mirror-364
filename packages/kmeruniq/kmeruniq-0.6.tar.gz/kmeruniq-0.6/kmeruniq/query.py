from kmeruniq.cli import subparsers
from kmeruniq.index import Index
from kmeruniq.parsing import read_file
from pathlib import Path
from vizibridge import DNA
import json
import tqdm
from itertools import chain
import sys


def query(args):
    if not args.count and not args.print:
        args.count = True
    if not args.index_path.exists():
        raise ValueError(f"Index path {args.index_path} do not exits")
    data_json = args.index_path / "data.json"
    if not data_json.exists():
        raise ValueError("Index path do not contains a data.json file")
    with open(data_json) as f:
        data = json.load(f)
    k = data["k"]
    it = iter(())
    if args.query_str:
        it = chain(it, DNA.from_str(args.query_str))
    if args.query_file:
        it = chain(read_file(args.query_file))
    if not args.no_filter_duplicate:
        print(f"Eliminating duplicate kmers", file=sys.stderr)
        kmer_set = set()
        for dna in it:
            kmer_set.update(dna.enum_canonical_kmer(k))
        kmer_it = iter(kmer_set)
        print(f"Found {len(kmer_set)} uniq kmers", file=sys.stderr)
    else:
        kmer_it = (kmer for dna in it for kmer in dna.enum_canonical_kmer(k))
    index = Index(args.index_path)
    counter = {}
    for kmer in tqdm.tqdm(kmer_it):
        val = index.get(kmer, "Missing")
        if args.print:
            print(kmer, val)
        if args.count:
            counter[val] = counter.get(val, 0) + 1
    if args.count:
        print(counter)


subparser = subparsers.add_parser(
    "query",
    help="Build an index",
)

subparser.add_argument("--query_file", "-f", help="file to query", type=Path)
subparser.add_argument(
    "--query_str",
    "-q",
    help="a string to query. Every non nucleotid symbols are considered as separator",
    type=str,
)


subparser.add_argument(
    "--index_path", "-o", help="directory of an index", type=Path, required=True
)

subparser.add_argument("--count", "-c", help="Count the results", action="store_true")

subparser.add_argument("--print", "-p", help="Print the results", action="store_true")

subparser.add_argument(
    "--no-filter-duplicate",
    "-d",
    help="""Prevent the filtering of duplicate kmer.
To use in case where the input query file do not have duplicate kmers by construction.
For instance, if it is a bcalm file.""",
    action="store_true",
)

subparser.set_defaults(func=query)
