from typing import Annotated

from loguru import logger
from pydantic import BaseModel, Field, StringConstraints
from requests.exceptions import HTTPError

from metabintools.ena_taxonomy.ena_taxonomy import EnaSubmittableTaxonomy


class BinTaxonomy(BaseModel):
    tax_source: str = Field(..., description="Source of the taxonomy classification")
    tax_classification: Annotated[
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
    taxon_name: str | None = Field(None, description="Taxonomic name for the bin")
    taxid: int | None = Field(None, ge=1, description="Taxonomic ID for the bin")

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
            self._generate_taxon_name()

    def _generate_taxon_name(self) -> None:
        """Returns the computed taxon name, based on the classification string."""
        parsed_classification = self._parse_classification()

        if self.tax_source == "ncbi":
            try:
                taxon_name = EnaSubmittableTaxonomy().ena_suggest_lineage_taxid(
                    lineage=self.tax_classification
                )
                if taxon_name:
                    self.taxid = taxon_name.get("taxId")
                    self.taxon_name = taxon_name.get("scientificName")
                    return
            except (HTTPError, ValueError) as e:
                logger.warning(f"Failed to generate submittable taxon name: {e}")

        order = ["s", "g", "f", "o", "c", "p", "k", "d"]

        for rank in order:
            if rank in parsed_classification:
                value = parsed_classification[rank]
                if value:
                    if rank == "s":
                        self.taxon_name = value
                    else:
                        self.taxon_name = f"{value} sp."
                    return

    def _parse_classification(self) -> dict[str, str | None]:
        """
        Parse the classification string into a dictionary of taxonomic parts.

        Returns:
            A dictionary mapping taxonomic parts to their values.
        """
        parts = {}
        for part in self.tax_classification.split(";"):
            if "__" in part:
                key, val = part.split("__", 1)
                parts[key.strip()] = val.strip() if val.strip() else None
        return parts
