from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, field_validator

from bintools.enums import Frame, Strand


class Annotation(BaseModel):
    seqname: str
    source: str
    feature: str
    start: int = Field(..., gt=0)
    end: int = Field(..., gt=0)
    score: float | None = None
    strand: Strand
    frame: Frame
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("end")
    @classmethod
    def validate_end_greater_than_start(cls, v, info):
        if "start" in info.data and v < info.data["start"]:
            raise ValueError("end must be greater than or equal to start")
        return v

    def to_gff_record(self) -> str:
        """
        Formats the annotation as a GFF record (tab-delimited line).

        Returns:
            A GFF-formatted string ready to write to file.
        """
        logger.debug(f"Formatting annotation: {self.seqname}, {self.feature}")

        # Format attributes as key=value pairs separated by semicolons
        attr_parts = []
        for key, value in self.attributes.items():
            attr_parts.append(f"{key}={value}")
        attributes_str = ";".join(attr_parts) if attr_parts else ""

        # Format score (. if None)
        score_str = str(self.score) if self.score is not None else "."

        # Build the GFF record
        record = "\t".join(
            [
                self.seqname,
                self.source,
                self.feature,
                str(self.start),
                str(self.end),
                score_str,
                str(self.strand),
                str(self.frame),
                attributes_str,
            ]
        )

        return record
