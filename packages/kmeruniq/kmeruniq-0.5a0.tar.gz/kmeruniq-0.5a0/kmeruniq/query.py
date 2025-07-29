from kmeruniq.cli import subparsers
from kmeruniq.index import Index
from kmeruniq.parsing import read_file
from pathlib import Path
from vizibridge import DNA
from collections import Counter
import json
import tqdm


def query(args):
    if not args.index_path.exists():
        raise ValueError(f"Index path {args.index_path} do not exits")
    data_json = args.index_path / "data.json"
    if not data_json.exists():
        raise ValueError("Index path do not contains a data.json file")
    with open(data_json) as f:
        data = json.load(f)
    k = data["k"]
    kmer_set = set()
    if args.query_str:
        kmer_set.update(
            *(dna.enum_canonical_kmer(k) for dna in DNA.from_str(args.query_str))
        )
    if args.query_file:
        for dna in tqdm.tqdm(read_file(args.query_file)):
            kmer_set.update(dna.enum_canonical_kmer(k))
    print(f"Found {len(kmer_set)} kmers")
    index = Index(args.index_path)
    cnt = Counter(index.get(kmer, "Missing") for kmer in kmer_set)
    print(cnt)


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
subparser.set_defaults(func=query)
