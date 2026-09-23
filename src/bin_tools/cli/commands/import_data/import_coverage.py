from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.enums import CoverageTool
from bin_tools.export.binset_exporter import BinSetExporter


@click.command("coverage")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--tool",
    type=click.Choice(CoverageTool),
    help="Tool used to estimate coverage",
    required=False,
    default=CoverageTool.metabat,
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
@click.argument("binfile", type=click.File("rb"), required=True, default="-")
@click.argument(
    "coverage",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Coverage file with contig-level coverage information",
    required=True,
)
def import_coverage(
    binfile: IO,
    coverage: str,
    output: IO,
    tool: CoverageTool,
    compress: bool = False,
):
    """Add quality scores to a BINS file from a coverage file.

    The coverage file must come from Metabat2's jgi_summarize_bam_depths script.

    BINFILE: a BINS file to add the coverage to
    """
    try:
        logger.info("Reading binfile...")
        binset = BinSet.read_binfile(binfile)

        logger.info(f"Adding coverage data from {Path(coverage).name}...")
        out_binset = binset.add_contig_coverage(Path(coverage), tool)

        logger.info("Updating statistics...")
        out_binset = out_binset.update_statistics()

        logger.info("Writing binfile...")
        BinSetExporter(out_binset).write_binfile(output, compress=compress)
        logger.info("Coverage import completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
