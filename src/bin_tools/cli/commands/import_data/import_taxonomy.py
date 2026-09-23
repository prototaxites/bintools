from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.enums import TaxonomyTool


@click.command("taxonomy")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--tool",
    type=click.Choice(TaxonomyTool),
    help="Tool used to assign taxonomy to the bins",
    required=True,
    default=TaxonomyTool.MANUAL,
)
@click.option(
    "--taxonomy",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Input file containing bin-level taxonomy information",
    required=True,
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
@click.argument("binfile", type=click.File("rb"), required=True, default="-")
def import_taxonomy(
    binfile: IO,
    output: IO,
    taxonomy: str,
    tool: TaxonomyTool,
    compress: bool = False,
):
    """Add a set of quality scores to a BINS file.

    BINFILE: a BINS file to add the bins to
    """
    try:
        logger.info("Reading binfile...")
        binset = BinSet.read_binfile(binfile)

        if binset.bins is None:
            logger.error("No bins found in the BINS file.")
            raise click.ClickException("No bins found in the BINS file.")

        logger.info(f"Adding taxonomy from {Path(taxonomy).name}...")
        out_binset = binset.add_bin_taxonomy(Path(taxonomy), tool)

        logger.info("Writing binfile...")
        out_binset.write_binfile(output, compress=compress)
        logger.info("Taxonomy import completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
