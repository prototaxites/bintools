from enum import StrEnum


class Strand(StrEnum):
    FORWARD = "+"
    REVERSE = "-"
    UNSTRANDED = "."


class Frame(StrEnum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    UNSPECIFIED = "."


class Assembler(StrEnum):
    spades = "spades"
    megahit = "megahit"
    flye = "flye"
    metamdbg = "metamdbg"
    myloasm = "myloasm"
    hifiasm_meta = "hifiasm_meta"


class MiMAG(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class QualityTool(StrEnum):
    CHECKM = "checkm"
    CHECKM2 = "checkm2"
    BUSCO = "busco"
    MANUAL = "manual"
