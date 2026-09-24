import click

from metabintools.cli.commands.summarise.bins import summarise_bins
from metabintools.cli.commands.summarise.contigs import summarise_contigs
from metabintools.cli.commands.summarise.group import summarise_groups


@click.group()
def summarise_group():
    """
    Tools for summarising BINS files.
    """


summarise_group.add_command(summarise_bins)
summarise_group.add_command(summarise_contigs)
summarise_group.add_command(summarise_groups)
