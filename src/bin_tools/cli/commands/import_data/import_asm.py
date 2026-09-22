from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.enums import Assembler
from bin_tools.import_data.assembly import parse_assembly_fasta


@click.command("asm")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--assembler",
    type=click.Choice(Assembler),
    help="(optional) Name of the assembler used to produce the assembly.",
    required=False,
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
@click.argument(
    "assembly", type=click.Path(exists=True, dir_okay=False, file_okay=True)
)
def import_assembly(
    assembly: str, assembler: Assembler | None, output: IO, compress: bool = False
):
    """Import a metagenome assembly to initialise a BINS file.

    ASSEMBLY: an (optionally gzip compressed) FASTA file containing the assembly.
    """
    logger.info(f"Parsing assembly: {Path(assembly).name}")
    try:
        parsed_assembly = parse_assembly_fasta(
            Path(assembly),
            assembler,
        )
    except RuntimeError as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(f"Error: {e}")

    logger.info(f"Parsed assembly: {Path(assembly).name}")

    binset = BinSet(contigs=parsed_assembly, bins=None)
    binset.write_binfile(output, compress=compress)
