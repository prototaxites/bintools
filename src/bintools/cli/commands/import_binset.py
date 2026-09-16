from pathlib import Path

import click

from bintools.enums import Assembler
from bintools.import_binset.assembly_parser import AssemblyParser


@click.command("import")
@click.option(
    "--assembly",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Path to the assembly file.",
)
@click.option(
    "--name",
    type=str,
    help="Name of the sample used to produce the assembly.",
)
@click.option(
    "--assembler",
    type=click.Choice(Assembler),
    help="Name of the assembler used to produce the assembly.",
)
@click.argument("bindir", type=click.Path(exists=True, dir_okay=True, file_okay=False))
def import_binset(assembly: str, name: str, assembler: Assembler, bindir: str):
    """Create a BINS file from a directory of bins and a metagenome assembly."""
    parsed_assembly = AssemblyParser(
        Path(assembly),
        assembler,
        name,
    )
    parsed_bins = BinParser(Path(bindir))
