# A tool to store kmer unique to dataset

To install:

```
pip install kmeruniq 
```

Two commands:

- `kmeruniq build`
- `kmeruniq query` 

Check the help with `-h` flag.

## Usage example of the CLI

```
kmeruniq build -k 21 --fof my_file.fof --output path/to/index -e --shard 20 
kmeruniq query --query_str ACGAAACGTACATTCACACACACACATAGAGAAGGAGAGCAGCACACACA --index-path path/to/index
kmeruniq query --query_file path/to/some/data.fa --index-path path/to/index
```

The output is a the result of a Counter for each value.


## The fof format

A file of file. That is a line separated list of file.

```
/path/to/foo.fa
/path/to/bar.fa
/path/to/barrr.fa.gz
```

Each line can also specify a label for the file. Two file with the same label will be considered
as merge. For instance:


```
/path/to/foo.fa     ;chr1
/path/to/bar.fa     ;chr2
/path/to/barrr.fa.gz   ;chr1
```

Here the `foo.fa` and `barr.fa.gz` will be merged together within the index.

Remark that file can be gzip compressed.

## Usage example of the Python API:

The Kmer and DNA datatype are the one used by vizibridge.

```python
from kmeruniq.index import Index
from vizibridge import Kmer, DNA

idx = Index("path/to/my/index")
# idx is a dict-like object keyed by kmer and valued by the annotation

idx["ACG..ACG"] # some kmer of the appropriate size. 

for kmer in idx:
    print(idx[kmer]) # print the value of each kmer

dna = DNA("ACG....ACGT") # long sequence of DNA from somewhere

for kmer in dna.enum_canonical_kmer(idx.k):
    print(idx.get(kmer)) # print the value associated to kmer or None if kmer not inside.

```

