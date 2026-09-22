from pathlib import Path

from loguru import logger

from bin_tools.dataclasses.annotation import Annotation, Frame, Strand
from bin_tools.dataclasses.contig import Contig


def read_gff(gff: Path) -> dict[str, list[Annotation]]:
    """Parse a GFF3 file into a list of Annotation objects.

    Args:
        gff (Path): The path to the GFF3 file.

    Returns:
        dict[str, list[Annotation]]: A dictionary mapping seqnames to lists of annotations.
    """
    annotations = {}

    with open(gff) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            fields = line.split("\t")
            if len(fields) < 8:
                logger.debug(f"Error parsing line: {line}")
                continue

            attributes = {}
            if len(fields) > 8:
                for attr in fields[8].split(";"):
                    if "=" in attr:
                        key, val = attr.split("=", 1)
                        attributes[key.strip()] = val.strip()

            try:
                annotation = Annotation(
                    seqname=fields[0],
                    source=fields[1],
                    feature=fields[2],
                    start=int(fields[3]),
                    end=int(fields[4]),
                    score=float(fields[5]) if fields[5] != "." else None,
                    strand=Strand(fields[6]),
                    frame=Frame(fields[7]),
                    attributes=attributes,
                )
                seqname = fields[0]
                if seqname not in annotations:
                    annotations[seqname] = []
                annotations[seqname].append(annotation)
            except (ValueError, KeyError) as e:
                logger.debug(f"Error parsing annotation: {line}\n with error: {e}")
                continue

    return annotations


def annotate_contigs(
    contigs: dict[str, Contig], gff: Path, overwrite: bool = False
) -> dict[str, Contig]:
    """
    Annotate contigs with GFF3 annotations.

    Args:
        contigs (dict[str, Contig]): The contigs to annotate.
        gff (Path): The path to the GFF3 file.
        overwrite (bool): Whether to overwrite existing annotations.

    Returns:
        dict[str, Contig]: Contigs with annotations.
    """
    annotations = read_gff(gff)

    return {
        contig_id: contig.model_copy(
            update={
                "annotations": _merge_annotations(
                    contig, annotations.get(contig_id), overwrite
                )
            }
        )
        for contig_id, contig in contigs.items()
    }


def _merge_annotations(contig: Contig, new_annotations, overwrite: bool):
    """Determine which annotations to use for a contig."""
    if overwrite:
        return new_annotations
    if new_annotations is None:
        return contig.annotations
    return (
        contig.annotations + new_annotations if contig.annotations else new_annotations
    )
