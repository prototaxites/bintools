import re
from pathlib import Path

import pyfastx
from loguru import logger

from bin_tools.dataclasses.contig import Contig
from bin_tools.enums import Assembler


def parse_assembly_fasta(
    assembly: Path, assembler: Assembler | None
) -> dict[str, Contig]:
    """
    Parse an assembly FASTA file into a list of Contig objects.

    Args:
        assembly: The path to the assembly FASTA file.
        assembler: The assembler used to generate the assembly.

    Returns:
        A list of Contig objects.
    """
    _CIRCULAR_REGEX = {
        "myloasm": re.compile(r"circular-yes|circular-possibly"),
        "metamdbg": re.compile(r"circular=yes"),
    }

    parser = pyfastx.Fastx(str(assembly), comment=True)
    topology_regex = _CIRCULAR_REGEX.get(str(assembler))

    names = set()
    contigs = {}

    for id, seq, comment in parser:
        if id in names:
            raise ValueError(f"Duplicate sequence id: {id}")
        names.add(id)

        topology = "linear"
        if topology_regex and topology_regex.search(f"{id} {comment}"):
            topology = "circular"

        logger.debug(f"ADDING CONTIG: {id}, topology={topology}")

        sequence = seq.upper()
        contig = Contig(
            id=id,
            header=f"{id} {comment}",
            sequence=sequence,
            sequence_length=len(sequence),
            topology=topology,
        )
        contigs[id] = contig

    return contigs
