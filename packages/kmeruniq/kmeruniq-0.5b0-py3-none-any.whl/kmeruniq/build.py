from kmeruniq.cli import subparsers
from kmeruniq.parsing import read_file
import json
from pathlib import Path
from vizibridge import KmerIndex, DNA, KmerTypeMap
from typing import Iterator
import os
from multiprocessing import Process
import argparse
import tempfile
import shutil
import tqdm


def generator(files: dict[Path, int], verbose=False) -> Iterator[tuple[DNA, int]]:
    items = files.items()
    if verbose:
        curr, total = verbose
        tqdm_inst = tqdm.tqdm(total=total)
        tqdm_inst.update(curr)

    for file, val in items:
        data = read_file(file)
        if verbose:
            tqdm_inst.update(1)
        yield from ((dna, val) for dna in data)


def generate_index(iterator, k, tmp_path, out_path, index, shards):
    idx = KmerIndex.build_dna(iterator, tmp_path, k, index, shards)
    idx.extract_uniq(out_path)


def build(args):
    if not args.fof.exists():
        raise ValueError(f"{args.files} do not exists")
    if args.output.exists():
        if args.erase:
            shutil.rmtree(args.output)
            args.output.mkdir()
        else:
            raise ValueError(f"{args.output} already exits")
    else:
        args.output.mkdir()
    try:
        files = dict()
        int_map = dict()
        with open(args.fof) as f:
            for i, elem in enumerate(f.read().strip().split("\n")):
                if ";" in elem:
                    file, val = elem.split(";")
                else:
                    file, val = elem, Path(elem).name
                path = Path(file)
                if not path.exists():
                    raise ValueError(f"{path} do not exists (line {i})")
                if path in files:
                    raise ValueError(f"{path} twice in the file of file (line {i})")
                if val not in int_map:
                    int_map[val] = len(int_map)
                files[path] = int_map[val]
        if args.temp_dir and not args.temp_dir.exists():
            raise ValueError(f"tmp_dir is set to a non-existing dir {args.temp_dir}")
        with tempfile.TemporaryDirectory(dir=args.temp_dir) as tmpdirname:
            process = []
            tmp_dir = Path(tmpdirname)
            total = (args.shards // args.process_nb) * len(files)
            curr = 0
            inst_tqdm = tqdm.tqdm(total=args.shards)
            for shard_index in range(args.shards):
                tmp_shard_path = tmp_dir / str(shard_index)
                out_shard_path = args.output / str(shard_index)
                verbose = False
                if shard_index % args.process_nb == 0:
                    verbose = (curr, total)
                proc = Process(
                    target=generate_index,
                    args=(
                        generator(files, verbose=verbose),
                        args.k,
                        tmp_shard_path,
                        out_shard_path,
                        shard_index,
                        args.shards,
                    ),
                )
                proc.start()
                process.append(proc)
                if (shard_index + 1) % args.process_nb == 0:
                    for proc in process:
                        proc.join()
                        curr += len(files)
                        if proc.exitcode != 0:
                            raise ValueError(
                                f"Process exited with code {proc.exitcode}"
                            )
                    process = []

            for proc in process:
                proc.join()
                inst_tqdm.update(1)

        descr = {"k": args.k, "int_map": int_map, "shards": args.shards}
        with open(args.output / "data.json", "w") as f:
            json.dump(descr, f)
    except Exception as E:
        print("erasing")
        shutil.rmtree(args.output)
        raise E


subparser = subparsers.add_parser(
    "build", help="Build an index", formatter_class=argparse.RawTextHelpFormatter
)

fof_help = """
A file of file. That is a line separated list of file.

Each line can also specify a label for the file. Two file with the same label will be considered
as merge. For instance:


/path/to/foo.fa     ;chr1
/path/to/bar.fa     ;chr2
/path/to/barrr.fa.gz   ;chr1

Here the barr will be merged with foo.
File can be gzip compressed.
"""

kmer_help = f"""
Valid k are in {sorted(KmerTypeMap)}
"""

subparser.add_argument("-k", type=int, help=kmer_help, required=True)
subparser.add_argument("--fof", help=fof_help, type=Path, required=True)
subparser.add_argument(
    "--output",
    "-o",
    help="Output directory. Should not exists",
    type=Path,
    required=True,
)
subparser.add_argument(
    "--erase",
    "-e",
    help="Erase the output directory if exists",
    action="store_true",
    default=False,
)
subparser.add_argument("--shards", "-s", help="number of shards", type=int, default=1)
subparser.add_argument(
    "--process_nb", "-p", help="number of process", type=int, default=os.cpu_count() - 1
)

subparser.add_argument(
    "--temp_dir", "-t", help="temporary_directory", type=Path, default=None
)
subparser.set_defaults(func=build)
