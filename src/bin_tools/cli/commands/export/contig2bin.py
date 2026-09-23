from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.export.binset_exporter import BinSetExporter


@click.command("contig2bin")
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, file_okay=True, exists=False),
    required=True,
    default=".",
    help="Output file path for the contig2bin mapping",
)
@click.option(
    "-g",
    "--group",
    type=str,
    help="Write bins from a specific group (if not specified, all bins are included)",
)
@click.argument(
    "binfile",
    type=click.File("rb"),
    nargs=1,
    required=True,
    default="-",
    help="Input binfile to export (use '-' for stdin)",
)
def contig2bin(
    binfile: IO,
    output: str,
    group: str | None = None,
):
    """Write stored bin annotations to a set of GFF files.

    BINFILE: Path to the binfile to write GFFs for.
    """
    try:
        logger.info(f"Reading binfile from {binfile.name}...")
        binset = BinSet.read_binfile(binfile)

        output_path = Path(output)
        logger.info(f"Writing contig2bin mapping to {output_path}")

        BinSetExporter(binset).export_contig2bin(
            path=output_path,
            group=group,
        )

        logger.info("Contig2bin export completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
