from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from bin_tools.dataclasses.annotation import Annotation


class Contig(BaseModel):
    id: str = Field(..., description="Contig ID.")
    header: str = Field(..., description="Full contig header including ID.")
    sequence: Annotated[str, StringConstraints(pattern=r"^[ACGTN]+$")] = Field(
        ..., description="Sequence of the contig."
    )
    sequence_length: Annotated[int, Field(gt=0)] = Field(
        ..., description="Length of the sequence."
    )
    topology: Literal["linear", "circular"] | None = Field(
        None, description="Topology of the contig."
    )
    coverage: Annotated[float, Field(gt=0)] | None = Field(
        None, description="Depth of the contig in the originating sample."
    )
    annotations: list[Annotation] | None = Field(
        None, description="Annotations of the contig."
    )
