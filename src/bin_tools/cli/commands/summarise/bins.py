from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.export.binset_exporter import BinSetExporter


@click.command("bins")
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    required=True,
    help="Output TSV file path for bin summary",
)
@click.option(
    "--include-statistics",
    "-s",
    is_flag=True,
    help="(optional) Include statistics in the output.",
)
@click.option(
    "--include-taxonomy",
    "-t",
    is_flag=True,
    help="(optional) Include taxonomy in the output.",
)
@click.argument(
    "binfile",
    type=click.File("rb"),
    nargs=1,
    required=True,
)
def summarise_bins(
    binfile: IO,
    output: str,
    include_statistics: bool = False,
    include_taxonomy: bool = False,
):
    """Write a summary of the bins in the binfile to the output.

    BINFILE: Path to the binfile to summarise
    """
    try:
        logger.info("Reading binfile(s)...")
        binset = BinSet.read_binfile(binfile)

        output_path = Path(output)
        logger.info(f"Writing bin summary to {output_path}")

        BinSetExporter(binset).write_bin_summary_tsv(
            output_path=output_path,
            include_statistics=include_statistics,
            include_taxonomy=include_taxonomy,
        )

        logger.info("Bin summary completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
