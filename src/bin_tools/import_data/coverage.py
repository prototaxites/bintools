import csv
from pathlib import Path
from turtle import st

from loguru import logger

from bin_tools.dataclasses.contig import Contig
from bin_tools.enums import CoverageTool


class CoverageReader:
    @staticmethod
    def _read_jgi_summarise_contig_depths(coverage_file: Path) -> dict[str, float]:
        coverage: dict[str, float] = {}
        with open(coverage_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contig_name = row["contigName"]
                coverage[contig_name] = float(row["totalAverageDepth"])

        return coverage

    def add_coverage(
        self,
        contigs: dict[str, Contig],
        coverage_file: Path,
        coverage_tool: CoverageTool,
    ) -> dict[str, Contig]:
        if coverage_tool == "metabat":
            coverages = self._read_jgi_summarise_contig_depths(coverage_file)
        else:
            logger.error(f"Unknown coverage format: {coverage_tool}")
            return contigs

        return {
            contig_id: contig.model_copy(
                update={"coverage": coverages.get(contig_id, None)}
            )
            for contig_id, contig in contigs.items()
        }
