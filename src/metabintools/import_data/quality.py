import csv
from pathlib import Path

from loguru import logger

from metabintools.bin_utils import get_basename
from metabintools.dataclasses.bin import Bin, BinStatistics
from metabintools.enums import QualityTool


class QualityReader:
    @staticmethod
    def _parse_quality_csv(
        file: Path,
        bin_id_col: str,
        completeness_col: str,
        contamination_col: str,
        is_percentage: bool = False,
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
                if is_percentage:
                    results[bin_id] = (
                        results[bin_id][0] / 100,
                        results[bin_id][1] / 100,
                    )
        return results

    def add_quality_scores(
        self, bins: list[Bin], quality_file: Path, qc_tool: QualityTool
    ) -> list[Bin]:
        """
        Add quality information to the bins based on the quality file and QC tool.

        Args:
            bins (list[Bin]): The list of bins to update.
            quality_file (Path): The path to the quality file.
            qc_tool (QualityTool): The QC tool used to generate the quality file.

        Returns:
            list[Bin]: The updated list of bins with quality information.
        """
        if qc_tool == QualityTool.checkm:
            results = self._parse_quality_csv(
                quality_file,
                "Bin Id",
                "completeness",
                "contamination",
                is_percentage=True,
            )
        elif qc_tool == QualityTool.checkm2:
            results = self._parse_quality_csv(
                quality_file,
                "Name",
                "Completeness",
                "Contamination",
                is_percentage=True,
            )
        elif qc_tool == QualityTool.busco:
            results = self._parse_quality_csv(
                quality_file, "Input_file", "Complete", "Duplicated", is_percentage=True
            )
        else:
            results = self._parse_quality_csv(
                quality_file,
                "File",
                "Completeness",
                "Contamination",
                is_percentage=True,
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
                        "quality_tool": qc_tool,
                    }
                )
                out_bin = bin.model_copy(update={"statistics": statistics})
                out_bins.append(out_bin)
            else:
                logger.info(f"No quality data found for bin {bin.id}")
                out_bins.append(bin)

        return out_bins
