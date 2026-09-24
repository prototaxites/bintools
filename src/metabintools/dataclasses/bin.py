import gzip
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

from metabintools.binstatistics import CalculateBinStatistics
from metabintools.dataclasses.bin_statistics import BinStatistics
from metabintools.dataclasses.bin_taxonomy import BinTaxonomy
from metabintools.dataclasses.contig import Contig


class Bin(BaseModel):
    id: str = Field(..., description="Name of the bin.")
    import_name: str = Field(
        ..., frozen=True, description="File the bin was imported from."
    )
    group: str = Field(..., description="Group the bin belongs to, e.g. a binner.")
    contigs: list[str] = Field(..., description="List of contig IDs in the bin.")
    statistics: BinStatistics | None = Field(
        None, description="Statistics for the bin."
    )
    taxonomy: BinTaxonomy | None = Field(None, description="Taxonomy for the bin.")

    def update_statistics(
        self,
        contig_dict: dict[str, Contig],
    ) -> "Bin":
        """
        Updates all bin statistics.

        Args:
            contig_dict: Dictionary mapping contig IDs to `Contig` instances.

        Returns:
            The updated `Bin` instance with populated statistics.
        """
        bin_contigs = {cid: contig_dict[cid] for cid in self.contigs}

        statistics = (
            self.statistics.model_copy() if self.statistics else BinStatistics()
        )

        statistics.length = CalculateBinStatistics.bin_size(bin_contigs)
        statistics.longest = CalculateBinStatistics.bin_longest_contig(bin_contigs)
        statistics.n_contigs = len(bin_contigs)
        statistics.n_circular = CalculateBinStatistics.bin_n_circular(bin_contigs)
        statistics.n50 = CalculateBinStatistics.bin_n50(bin_contigs)
        statistics.coverage = CalculateBinStatistics.bin_coverage(bin_contigs)
        statistics.n_unique_trnas = CalculateBinStatistics.bin_n_unique_trnas(
            bin_contigs
        )
        statistics.has_5s = CalculateBinStatistics.bin_has_5s(bin_contigs)
        statistics.has_16s = CalculateBinStatistics.bin_has_16s(bin_contigs)
        statistics.has_23s = CalculateBinStatistics.bin_has_23s(bin_contigs)
        statistics.update_mimag()

        return self.model_copy(update={"statistics": statistics})

    def export_fasta(
        self,
        contig_dict: dict[str, Contig],
        output_dir: Path,
        preserve_headers: bool = False,
        compress: bool = True,
    ) -> None:
        """
        Writes the bin as a FASTA file.

        Args:
            contig_dict: Dictionary of contigs.
            output_dir: Path to the directory to write FASTA files.
            preserve_headers: Whether to preserve the contig headers in the output.
            compress: Whether to compress the output file using gzip.
        """
        bin_contigs = {cid: contig_dict[cid] for cid in self.contigs}

        outfile = output_dir / (f"{self.id}.fa" + (".gz" if compress else ""))
        open_func = gzip.open if compress else open

        with open_func(outfile, "wt") as f:
            for contig in bin_contigs.values():
                logger.debug(f"Writing contig {contig.id}")
                header = contig.header if preserve_headers else contig.id
                f.write(f">{header}\n{contig.sequence}\n")

    def export_gff(
        self,
        contig_dict: dict[str, Contig],
        output_dir: Path,
    ) -> None:
        """
        Writes the bin annotations to a GFF file.

        Args:
            contig_dict: Dictionary of contigs.
            output_dir: Path to the directory to write GFF files.
        """
        bin_annotations = [
            annotation
            for cid in self.contigs
            if (annotations := contig_dict[cid].annotations) is not None
            for annotation in annotations
        ]

        if len(bin_annotations) == 0:
            logger.warning(f"No annotations found for bin {self.id}, skipping.")
            return

        outfile = output_dir / f"{self.id}.gff"

        with open(outfile, "wt") as f:
            f.write("##gff-version 3\n")
            f.writelines(
                annotation.to_gff_record() + "\n" for annotation in bin_annotations
            )
