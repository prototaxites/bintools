from pydantic import BaseModel, field_validator


class Contig(BaseModel):
    sample_id: str
    id: str
    header: str
    sequence: str
    sequence_hash: str
    sequence_length: int
    topology: str | None = None
    depth: float | None = None
    trnas: list[str] | None = None
    rrna_5s: bool | None = None
    rrna_16s: bool | None = None
    rrna_23s: bool | None = None


class Bin(BaseModel):
    sample_id: str
    id: str
    contigs: list[str]
    taxon: str | None = None
    lineage: str | None = None
    taxonomy_origin: str | None = None
    completeness: float | None = None
    contamination: float | None = None


class BinSet(BaseModel):
    assembly: list[Contig]
    bins: list[Bin]

    @property
    def bin_contig_ids(self) -> set[str]:
        return {contig_id for bin in self.bins for contig_id in bin.contigs}

    @property
    def assembly_contig_ids(self) -> set[str]:
        return {contig.id for contig in self.assembly}

    @field_validator("bins")
    def validate_bin_contigs(cls, bins, info):
        assembly_ids = {c.id for c in info.data["assembly"]}
        for bin in bins:
            missing = set(bin.contigs) - assembly_ids
            if missing:
                raise ValueError(f"Bin {bin.id} references missing contigs: {missing}")
        return bins
