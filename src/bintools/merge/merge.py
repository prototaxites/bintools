import sys

from loguru import logger

from bintools.dataclasses.binset import BinSet


def merge_binsets(binsets: list[BinSet]) -> BinSet:
    """
    Merge multiple BinSet objects into a single BinSet.

    Args:
        binsets (list[BinSet]): A list of BinSet objects to merge.

    Returns:
        BinSet: The merged BinSet object.
    """
    out_contigs = {}
    out_bins = {}

    for idx, binset in enumerate(binsets):
        logger.info(f"Processing bin set {idx}.")

        for contig_id, contig in binset.contigs.items():
            if (
                contig_id in out_contigs
                and out_contigs[contig_id].sequence != contig.sequence
            ):
                logger.error(f"Contig {contig_id} differs between binsets")
                sys.exit(1)

            logger.debug(f"Adding contig {contig_id}")
            out_contigs[contig_id] = contig

        if binset.bins is not None:
            for bin in binset.bins:
                if out_bins.get(bin.id) is not None:
                    logger.error("Bin {bin.id} is in two separate datasets!")
                    sys.exit(1)

                logger.debug(f"Adding bin {bin.id}")
                out_bins[bin.id] = bin

    return BinSet(contigs=out_contigs, bins=list(out_bins.values()))
