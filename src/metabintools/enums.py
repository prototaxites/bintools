from enum import StrEnum


class Strand(StrEnum):
    """Strand of a genomic feature."""

    FORWARD = "+"
    REVERSE = "-"
    UNSTRANDED = "."


class Frame(StrEnum):
    """GTF frames"""

    ZERO = "0"
    ONE = "1"
    TWO = "2"
    UNSPECIFIED = "."


class Assembler(StrEnum):
    """List of supported assemblers."""

    spades = "spades"
    megahit = "megahit"
    flye = "flye"
    metamdbg = "metamdbg"
    myloasm = "myloasm"
    hifiasm_meta = "hifiasm_meta"


class MiMAG(StrEnum):
    """MiMAG quality annotations"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class QualityTool(StrEnum):
    """Supported bin QC tools"""

    checkm = "checkm"
    checkm2 = "checkm2"
    busco = "busco"
    manual = "manual"


class TaxonomyTool(StrEnum):
    """Supported taxonomy tools."""

    gtdbtk = "gtdbtk"
    gtdbtk_ncbi = "gtdbtk_ncbi"
    manual = "manual"


class CoverageTool(StrEnum):
    """Supported coverage tools."""

    metabat = "metabat"
