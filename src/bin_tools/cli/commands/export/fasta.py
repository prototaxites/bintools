from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet


@click.command("fasta")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(dir_okay=True, file_okay=False),
    required=True,
    default=".",
    help="Output directory for FASTA files",
)
@click.option(
    "--preserve-headers",
    "-h",
    is_flag=True,
    help="(optional) Preserve headers in the output FASTA file.",
)
@click.option(
    "--group-fasta",
    "-g",
    is_flag=True,
    help="(optional) Write each FASTA in a subdirectory named after the bin's group.",
)
@click.argument(
    "binfile",
    type=click.File("rb"),
    nargs=1,
    required=True,
    default="-",
    help="Input binfile to export (use '-' for stdin)",
)
def fasta(
    binfile: IO,
    outdir: str,
    compress: bool = False,
    preserve_headers: bool = False,
    group_fasta: bool = False,
):
    """Export a BINS file to FASTA.

    BINFILE: Path to the binfile to export FASTA for.
    """
    try:
        logger.info(f"Reading binfile from {binfile.name}...")
        binset = BinSet.read_binfile(binfile)

        outdir_path = Path(outdir)
        if not outdir_path.exists():
            logger.info(f"Creating output directory: {outdir_path}")
            try:
                outdir_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create output directory: {e}")
                raise click.ClickException(
                    f"Failed to create output directory {outdir}: {e}"
                )

        logger.info(
            f"Exporting {len(binset.bins) if binset.bins else 0} bin(s) to FASTA..."
        )
        binset.export_fasta(
            outdir=outdir_path,
            compress=compress,
            preserve_headers=preserve_headers,
            group_fasta=group_fasta,
        )
        logger.info("FASTA export completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
