from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from bintools.dataclasses.annotation import Annotation


class Contig(BaseModel):
    id: str
    header: str
    sequence: Annotated[str, StringConstraints(pattern=r"^[ACGTN]+$")]
    sequence_length: Annotated[int, Field(gt=0)]
    topology: Literal["linear", "circular"] | None = None
    depth: Annotated[float, Field(gt=0)] | None = None
    annotations: list[Annotation] | None = None
