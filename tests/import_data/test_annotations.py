from pathlib import Path

import pytest

from bin_tools.dataclasses.annotation import Frame, Strand
from bin_tools.enums import Assembler
from bin_tools.import_data.annotation import annotate_contigs, read_gff
from bin_tools.import_data.assembly import parse_assembly_fasta

TEST_DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def assembly_file():
    """Path to the assembly FASTA file."""
    return TEST_DATA_DIR / "asm.fasta"


@pytest.fixture
def assembly_gff():
    """Path to the assembly GFF file."""
    return TEST_DATA_DIR / "asm.gff"


class TestReadGFF:
    def test_returns_dict_keyed_by_seqname(self, assembly_gff):
        result = read_gff(assembly_gff)
        assert isinstance(result, dict)
        assert "contig1" in result
        assert "contig2" in result

    def test_parses_correct_number_of_annotations(self, assembly_gff):
        result = read_gff(assembly_gff)
        assert len(result["contig1"]) == 21
        assert len(result["contig2"]) == 4

    def test_annotation_fields_parsed_correctly(self, assembly_gff):
        result = read_gff(assembly_gff)
        first_annotation = result["contig1"][0]
        assert first_annotation.seqname == "contig1"
        assert first_annotation.feature == "tRNA"
        assert first_annotation.start == 1
        assert first_annotation.end == 3
        assert first_annotation.strand == Strand.FORWARD
        assert first_annotation.frame == Frame.UNSPECIFIED

    def test_attributes_parsed_correctly(self, assembly_gff):
        result = read_gff(assembly_gff)
        first_annotation = result["contig1"][0]
        assert first_annotation.attributes["ID"] == "tRNA_1"
        assert first_annotation.attributes["product"] == "tRNA-Ala"

    def test_handles_missing_score(self, assembly_gff):
        result = read_gff(assembly_gff)
        annotation = result["contig1"][0]
        assert annotation.score is None


class TestAnnotateContigs:
    def test_returns_list_of_contigs(self, assembly_file, assembly_gff):
        contigs = parse_assembly_fasta(assembly_file, Assembler.metamdbg)
        result = annotate_contigs(contigs, assembly_gff)
        assert isinstance(result, dict)
        assert len(result) == 3

    def test_adds_annotations_to_matching_contigs(self, assembly_file, assembly_gff):
        contigs = parse_assembly_fasta(assembly_file, Assembler.metamdbg)
        result = annotate_contigs(contigs, assembly_gff)
        assert result["contig1"].annotations is not None
        assert len(result["contig1"].annotations) == 21

    def test_handles_multiple_contigs(self, assembly_file, assembly_gff):
        contigs = parse_assembly_fasta(assembly_file, Assembler.metamdbg)
        result = annotate_contigs(contigs, assembly_gff)
        assert len(result) == 3
        if result["contig1"].annotations is not None:
            assert len(result["contig1"].annotations) == 21
        else:
            pytest.fail("contig1 should have annotations")
        if result["contig2"].annotations is not None:
            assert len(result["contig2"].annotations) == 4
        else:
            pytest.fail("contig2 should have annotations")
        if result["contig3"].annotations is not None:
            pytest.fail("contig3 should not have annotations")
