import click

from metabintools.cli.commands.import_data.import_annotation import import_annotation
from metabintools.cli.commands.import_data.import_asm import import_assembly
from metabintools.cli.commands.import_data.import_bins import import_binset
from metabintools.cli.commands.import_data.import_coverage import import_coverage
from metabintools.cli.commands.import_data.import_quality import import_quality
from metabintools.cli.commands.import_data.import_taxonomy import import_taxonomy


@click.group()
def import_group():
    """
    Tools for importing data, both contig- and bin-level, into a BINS file.

    All BINS files begin by importing an assembly via `metabintools import asm`.
    """


import_group.add_command(import_assembly)
import_group.add_command(import_binset)
import_group.add_command(import_annotation)
import_group.add_command(import_coverage)
import_group.add_command(import_taxonomy)
import_group.add_command(import_quality)
