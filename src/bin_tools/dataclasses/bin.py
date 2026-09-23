import gzip
from pathlib import Path
from typing import Annotated

from loguru import logger
from pydantic import BaseModel, Field, StringConstraints, computed_field

from bin_tools.binstatistics import CalculateBinStatistics
from bin_tools.dataclasses.contig import Contig
from bin_tools.enums import MiMAG, QualityTool


class BinStatistics(BaseModel):
    length: int | None = Field(None, gt=0, description="Length of the bin in bp")
    longest: int | None = Field(
        None, gt=0, description="Length of the longest contig in the bin in bp"
    )
    n_contigs: int | None = Field(
        None, gt=0, description="Number of contigs in the bin"
    )
    n_circular: int | None = Field(
        None, ge=0, description="Number of circular contigs in the bin"
    )
    n50: int | None = Field(None, gt=0, description="N50 of the bin")
    coverage: float | None = Field(None, gt=0, description="Coverage of the bin")
    completeness: float | None = Field(
        None, gt=0, lt=1, description="Completeness of the bin"
    )
    contamination: float | None = Field(
        None, gt=0, lt=1, description="Contamination of the bin"
    )
    quality_tool: QualityTool | None = Field(
        None, description="Quality tool used to assess the bin"
    )
    n_unique_trnas: int | None = Field(
        None, description="Number of unique tRNAs in the bin"
    )
    has_5s: bool | None = Field(None, description="Whether the bin contains 5S rRNA")
    has_16s: bool | None = Field(None, description="Whether the bin contains 16S rRNA")
    has_23s: bool | None = Field(None, description="Whether the bin contains 23S rRNA")
    mimag: MiMAG | None = Field(None, description="MiMAG level of the bin")

    def update_mimag(self) -> None:
        """
        Update the MiMAG level of the bin based on the number of contigs, circularity, completeness, contamination, and unique tRNAs.
        """
        if (
            self.n_contigs is not None
            and self.n_circular is not None
            and self.completeness is not None
            and self.contamination is not None
            and self.n_unique_trnas is not None
            and self.has_5s is not None
            and self.has_16s is not None
            and self.has_23s is not None
        ):
            conditions = {
                MiMAG.HIGH: (
                    self.contamination <= 5
                    and self.n_unique_trnas >= 18
                    and self.has_5s
                    and self.has_16s
                    and self.has_23s
                    and (
                        (self.completeness >= 50 and self.n_contigs == self.n_circular)
                        or self.completeness >= 90
                    )
                ),
                MiMAG.MEDIUM: self.completeness >= 50 and self.contamination <= 10,
                MiMAG.LOW: True,
            }
            self.mimag = next(quality for quality, met in conditions.items() if met)

        else:
            self.mimag = None


class BinTaxonomy(BaseModel):
    source: str = Field(..., description="Source of the taxonomy classification")
    classification: Annotated[
        str,
        StringConstraints(
            pattern=r"^[dk]__.*;p__.*;c__.*;o__.*;f__.*;g__.*;s__.*$|^unknown$"
        ),
    ] = Field(
        ...,
        description="Taxonomy classification lineage string, with format k__;p__;c__;o__;f__;g__;s__",
    )
    tax_kingdom: str | None = Field(None, description="Taxonomic kingdom for the bin")
    tax_phylum: str | None = Field(None, description="Taxonomic phylum for the bin")
    tax_class: str | None = Field(None, description="Taxonomic class for the bin")
    tax_order: str | None = Field(None, description="Taxonomic order for the bin")
    tax_family: str | None = Field(None, description="Taxonomic family for the bin")
    tax_genus: str | None = Field(None, description="Taxonomic genus for the bin")
    tax_species: str | None = Field(None, description="Taxonomic species for the bin")

    def model_post_init(self, __context, /) -> None:
        """Parse lineage and populate taxonomy fields if not provided.

        Args:
            __context: The context for the model post-init.
        """
        if not any(
            [
                self.tax_kingdom,
                self.tax_phylum,
                self.tax_class,
                self.tax_order,
                self.tax_family,
                self.tax_genus,
                self.tax_species,
            ]
        ):
            parsed = self._parse_classification()
            self.tax_kingdom = parsed.get("k") if parsed.get("k") else parsed.get("d")
            self.tax_phylum = parsed.get("p")
            self.tax_class = parsed.get("c")
            self.tax_order = parsed.get("o")
            self.tax_family = parsed.get("f")
            self.tax_genus = parsed.get("g")
            self.tax_species = parsed.get("s")

    @computed_field
    @property
    def taxon_name(self) -> str | None:
        """Returns the computed taxon name, based on the classification string."""
        parsed_classification = self._parse_classification()

        order = ["s", "g", "f", "o", "c", "p", "k", "d"]

        for rank in order:
            if rank in parsed_classification:
                value = parsed_classification[rank]
                if value:
                    if rank == "s":
                        return value
                    else:
                        return f"{value} sp."

        return None

    def _parse_classification(self) -> dict[str, str | None]:
        """
        Parse the classification string into a dictionary of taxonomic parts.

        Returns:
            A dictionary mapping taxonomic parts to their values.
        """
        parts = {}
        for part in self.classification.split(";"):
            if "__" in part:
                key, val = part.split("__", 1)
                parts[key.strip()] = val.strip() if val.strip() else None
        return parts


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
