from vizibridge import DNA
from pathlib import Path
from typing import Iterator
import gzip


def extract_dna(f) -> Iterator[DNA]:
    buf = ""
    for line in f:
        line = line.decode()
        if line[0] == b">":
            if buf:
                yield from DNA.from_str(buf.upper())
            buf = ""
        else:
            buf += line

    yield from DNA.from_str(buf.upper())


def read_file(file: Path) -> Iterator[DNA]:
    if file.name.endswith(".gz"):
        with gzip.open(file) as f:
            yield from extract_dna(f)
    else:
        with open(file, "rb") as f:
            yield from extract_dna(f)
