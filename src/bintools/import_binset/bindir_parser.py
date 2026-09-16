from pathlib import Path

import pyfastx

from bintools.bin_utils import get_basename, get_extension
from bintools.dataclasses import Bin


class BinDirParser:
    def __init__(self, bindir: Path, sample_id: str):
        self._bins = []
        self.sample_id = sample_id

        bin_files = [
            p
            for p in Path(bindir).glob("*")
            if get_extension(p)
            in {".fa", ".fna", ".fasta", ".fa.gz", ".fna.gz", ".fasta.gz"}
        ]
        for bin in bin_files:
            self.parse_bin(bin)

    @property
    def bins(self):
        return self._bins

    def parse_bin(self, bin: Path):
        b = pyfastx.Fastx(bin)
        contigs = []
        for id, seq in b:
            contigs.append(id)

        bin_obj = Bin(
            sample_id=self.sample_id,
            id=get_basename(bin),
            contigs=contigs,
        )

        self._bins.append(bin_obj)
