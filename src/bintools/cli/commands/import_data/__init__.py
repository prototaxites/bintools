import click

from bintools.cli.commands.import_data.import_annotation import add_annotation
from bintools.cli.commands.import_data.import_asm import import_assembly
from bintools.cli.commands.import_data.import_bins import import_binset


@click.group()
def import_group():
    """
    Tools for importing data, both contig- and bin-level, into a BINS file.

    All BINS files begin by importing an assembly via `bintools import asm`.
    """


import_group.add_command(import_assembly)
import_group.add_command(import_binset)
import_group.add_command(add_annotation)
