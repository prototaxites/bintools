from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.export.binset_exporter import BinSetExporter


@click.command("contigs")
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    required=True,
    help="Output TSV file path for contig summary",
)
@click.argument(
    "binfile",
    type=click.File("rb"),
    nargs=-1,
    required=True,
)
def summarise_contigs(
    binfile: IO,
    output: str,
):
    """Write a summary of the bins in the binfile to the output.

    BINFILE: Path to the binfile to summarise
    """
    try:
        logger.info("Reading binfile(s)...")
        binset = BinSet.read_binfile(binfile)

        output_path = Path(output)
        logger.info(f"Writing contig summary to {output_path}")

        BinSetExporter(binset).write_contig_summary_tsv(output_path=output_path)

        logger.info("Contig summary completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
