import hashlib
import re
from pathlib import Path
from re import Pattern

import pyfastx

from bintools.dataclasses import Contig
from bintools.enums import Assembler


class AssemblyParser:
    def __init__(self, assembly: Path, assembler: Assembler, name: str):
        self._CIRCULAR_REGEX = {
            "myloasm": re.compile(r"circular-yes|circular-possibly"),
            "metamdbg": re.compile(r"circular=yes"),
        }

        self._assembly = []
        self.assembler = assembler
        self.name = name
        self.parse_assembly_fasta(assembly)

    @property
    def assembly(self):
        return self._assembly

    def _get_topology_regex(self, assembler: Assembler) -> Pattern[str] | None:
        if matcher := self._CIRCULAR_REGEX.get(str(assembler), None):
            return matcher
        return None

    def parse_assembly_fasta(self, assembly: Path):
        names = set()
        parser = pyfastx.Fastx(str(assembly), comment=True)
        topology_regex = self._get_topology_regex(self.assembler)

        for id, seq, comment in parser:
            if id in names:
                raise ValueError(f"Duplicate sequence id: {id}")

            topology = "linear"
            if topology_regex and topology_regex.search(f"{id} {comment}"):
                topology = "circular"

            sequence = seq.upper()
            contig = Contig(
                sample_id=self.name,
                id=id,
                header=f"{id} {comment}",
                sequence=sequence,
                sequence_hash=hashlib.blake2b(
                    sequence.encode(), digest_size=16
                ).hexdigest(),
                sequence_length=len(sequence),
                topology=topology,
            )
            self._assembly.append(contig)
