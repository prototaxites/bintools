from pathlib import Path
from typing import IO

import click
from loguru import logger

from metabintools.dataclasses.binset import BinSet
from metabintools.export.binset_exporter import BinSetExporter


@click.command("groups")
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    required=True,
    help="Output TSV file path for group summary",
)
@click.argument(
    "binfile",
    type=click.File("rb"),
    nargs=1,
    required=True,
)
def summarise_groups(
    binfile: IO,
    output: str,
):
    """Write an aggregated summary with the total count of bins per group, separated
    by MiMAG scores if available.

    BINFILE: Path to the binfile to summarise
    """
    try:
        logger.info("Reading binfile(s)...")
        binset = BinSet.read_binfile(binfile)

        output_path = Path(output)
        logger.info(f"Writing bin summary to {output_path}")

        BinSetExporter(binset).write_group_summary_tsv(
            output_path=output_path,
        )

        logger.info("Group summary completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
