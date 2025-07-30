from vizibridge import KmerIndex
from collections.abc import Mapping
from pathlib import Path
from vizibridge import Kmer
import json


class Index(Mapping):
    def __init__(self, path: Path | str):
        if isinstance(path, str):
            path = Path(path)
        data_path = path / "data.json"
        with open(data_path) as f:
            data = json.load(f)
        self.k = data["k"]
        self.data = data
        self.convert_int = {x: p for p, x in data["int_map"].items()}
        self.shards = [
            KmerIndex(path / f"{i}", self.k) for i in range(self.data["shards"])
        ]

    def items(self):
        yield from (shard.item() for shard in self.shards)

    def __iter__(self):
        for shard in self.shards:
            yield from shard

    def __len__(self):
        return sum(len(shard) for shard in self.shards)

    def __getitem__(self, kmer: Kmer | str) -> int:
        if isinstance(kmer, str):
            kmer = Kmer.from_sequence(kmer)
        n: int = len(self.shards)
        i = hash(kmer) % n
        shard = self.shards[i]
        return self.convert_int[shard[kmer]]

    def __contains__(self, kmer) -> bool:
        n: int = len(self.shards)
        i = hash(kmer) % n
        shard = self.shards[i]
        return kmer in shard
