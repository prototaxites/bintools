import csv
from pathlib import Path

from loguru import logger

from bin_tools.bin_utils import get_basename
from bin_tools.dataclasses.bin import Bin, BinStatistics
from bin_tools.enums import QualityTool


def _parse_quality_csv(
    file: Path,
    bin_id_col: str,
    completeness_col: str,
    contamination_col: str,
) -> dict[str, tuple[float, float]]:
    """Generic CSV parser for quality tools."""
    results = {}
    with open(file) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            bin_id = get_basename(Path(row[bin_id_col]))
            results[bin_id] = (
                float(row[completeness_col]),
                float(row[contamination_col]),
            )
    return results


def add_quality(bins: list[Bin], quality_file: Path, qc_tool: QualityTool) -> list[Bin]:
    """
    Add quality information to the bins based on the quality file and QC tool.

    Args:
        bins (list[Bin]): The list of bins to update.
        quality_file (Path): The path to the quality file.
        qc_tool (QualityTool): The QC tool used to generate the quality file.

    Returns:
        list[Bin]: The updated list of bins with quality information.
    """
    if qc_tool == QualityTool.CHECKM:
        results = _parse_quality_csv(
            quality_file, "Bin id", "completeness", "contamination"
        )
    elif qc_tool == QualityTool.CHECKM2:
        results = _parse_quality_csv(
            quality_file, "Name", "Completeness", "Contamination"
        )
    elif qc_tool == QualityTool.BUSCO:
        results = _parse_quality_csv(
            quality_file, "Input_file", "Complete", "Duplicated"
        )
    else:
        results = _parse_quality_csv(
            quality_file, "File", "Completeness", "Contamination"
        )

    out_bins = []
    for bin in bins:
        if bin.id in results:
            statistics = (
                bin.statistics.model_copy() if bin.statistics else BinStatistics()
            )
            completeness, contamination = results[bin.id]
            logger.debug(
                f"ADDING QUALITY: {bin.id}, completeness={completeness}, contamination={contamination}"
            )
            statistics = statistics.model_copy(
                update={
                    "completeness": completeness,
                    "contamination": contamination,
                }
            )
            out_bin = bin.model_copy(update={"statistics": statistics})
            out_bins.append(out_bin)
        else:
            logger.info(f"No quality data found for bin {bin.id}")
            out_bins.append(bin)

    return out_bins
