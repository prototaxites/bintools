import click

from bin_tools.cli.commands.summarise.bins import summarise_bins
from bin_tools.cli.commands.summarise.contigs import summarise_contigs


@click.group()
def summarise_group():
    """
    Tools for summarising BINS files.
    """


summarise_group.add_command(summarise_bins)
summarise_group.add_command(summarise_contigs)
