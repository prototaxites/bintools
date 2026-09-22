import gzip
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

from bintools.dataclasses.contig import Contig
from bintools.enums import MiMAG, QualityTool


class BinStatistics(BaseModel):
    length: int | None = Field(None, gt=0)
    longest: int | None = Field(None, gt=0)
    n_contigs: int | None = Field(None, gt=0)
    n_circular: int | None = Field(None, ge=0)
    n50: int | None = Field(None, gt=0)
    completeness: float | None = Field(None, gt=0, lt=1)
    contamination: float | None = Field(None, gt=0, lt=1)
    quality_tool: QualityTool | None = None
    unique_trnas: list[str] | None = Field(None)
    has_5s: bool | None = Field(None)
    has_16s: bool | None = Field(None)
    has_23s: bool | None = Field(None)
    mimag: MiMAG | None = MiMAG.UNKNOWN

    def update_mimag(self) -> None:
        if (
            self.n_contigs is not None
            and self.n_circular is not None
            and self.completeness is not None
            and self.contamination is not None
            and self.unique_trnas is not None
            and self.has_5s is not None
            and self.has_16s is not None
            and self.has_23s is not None
        ):
            conditions = {
                MiMAG.HIGH: (
                    self.contamination <= 5
                    and len(self.unique_trnas) >= 18
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
            self.mimag = MiMAG.UNKNOWN


class BinTaxonomy(BaseModel):
    source: str
    lineage: str
    kingdom: str | None = None
    phylum: str | None = None
    classs: str | None = None
    order: str | None = None
    family: str | None = None
    genus: str | None = None
    species: str | None = None

    def model_post_init(self, __context, /) -> None:
        """Parse lineage and populate taxonomy fields if not provided."""
        if not any(
            [
                self.kingdom,
                self.phylum,
                self.classs,
                self.order,
                self.family,
                self.genus,
                self.species,
            ]
        ):
            parsed = self._parse_lineage()
            self.kingdom = parsed.get("k")
            self.phylum = parsed.get("p")
            self.classs = parsed.get("c")
            self.order = parsed.get("o")
            self.family = parsed.get("f")
            self.genus = parsed.get("g")
            self.species = parsed.get("s")

    def _parse_lineage(self) -> dict[str, str]:
        parts = {}
        for part in self.lineage.split(";"):
            if "__" in part:
                key, val = part.split("__", 1)
                parts[key.strip()] = val.strip()
        return parts


class Bin(BaseModel):
    id: str = Field(...)
    import_name: str = Field(..., frozen=True)
    group: str = Field(...)
    contigs: list[str] = Field(...)
    statistics: BinStatistics | None = None
    taxonomy: BinTaxonomy | None = None

    @staticmethod
    def bin_size(contig_dict: dict[str, Contig]) -> int:
        return sum(contig.sequence_length for contig in contig_dict.values())

    @staticmethod
    def bin_n50(contig_dict: dict[str, Contig]) -> int:
        lengths = [contig.sequence_length for contig in contig_dict.values()]
        lengths.sort(reverse=True)
        total = sum(lengths)
        half = total // 2
        for length in lengths:
            if total >= half:
                return length
            total -= length
        return 0

    @staticmethod
    def bin_longest_contig(contig_dict: dict[str, Contig]) -> int:
        return max(contig.sequence_length for contig in contig_dict.values())

    @staticmethod
    def bin_n_circular(contig_dict: dict[str, Contig]) -> int:
        return sum(
            1 for contig in contig_dict.values() if contig.topology == "circular"
        )

    @staticmethod
    def bin_unique_trnas(contig_dict: dict[str, Contig]) -> list[str]:
        annotations = [a for c in contig_dict.values() for a in (c.annotations or [])]
        return list(
            {
                product
                for a in annotations
                if a.feature == "tRNA"
                and (product := a.attributes.get("product")) is not None
            }
        )

    @staticmethod
    def bin_has_5s(contig_dict: dict[str, Contig]) -> bool:
        annotations = [a for c in contig_dict.values() for a in (c.annotations or [])]
        return any(
            bool(a.attributes.get("product") in ["5S", "5S ribosomal RNA", "5S rRNA"])
            for a in annotations
            if a.feature == "rRNA"
        )

    @staticmethod
    def bin_has_16s(contig_dict: dict[str, Contig]) -> bool:
        annotations = [a for c in contig_dict.values() for a in (c.annotations or [])]
        return any(
            bool(
                a.attributes.get("product") in ["16S", "16S ribosomal RNA", "16S rRNA"]
            )
            for a in annotations
            if a.feature == "rRNA"
        )

    @staticmethod
    def bin_has_23s(contig_dict: dict[str, Contig]) -> bool:
        annotations = [a for c in contig_dict.values() for a in (c.annotations or [])]
        return any(
            bool(
                a.attributes.get("product") in ["23S", "23S ribosomal RNA", "23S rRNA"]
            )
            for a in annotations
            if a.feature == "rRNA"
        )

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

        statistics.length = Bin.bin_size(bin_contigs)
        statistics.longest = Bin.bin_longest_contig(bin_contigs)
        statistics.n_contigs = len(bin_contigs)
        statistics.n_circular = Bin.bin_n_circular(bin_contigs)
        statistics.unique_trnas = Bin.bin_unique_trnas(bin_contigs)
        statistics.has_5s = Bin.bin_has_5s(bin_contigs)
        statistics.has_16s = Bin.bin_has_16s(bin_contigs)
        statistics.has_23s = Bin.bin_has_23s(bin_contigs)
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
            output: Path to the output FASTA file.
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
            output: Path to the output GFF file.
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
