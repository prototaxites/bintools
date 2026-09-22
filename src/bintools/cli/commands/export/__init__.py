import click

from bintools.cli.commands.export.contig2bin import contig2bin
from bintools.cli.commands.export.fasta import fasta
from bintools.cli.commands.export.gff import gff


@click.group()
def export_group():
    """
    Tools for exporting data from a BINS file.
    """


export_group.add_command(contig2bin)
export_group.add_command(fasta)
export_group.add_command(gff)
