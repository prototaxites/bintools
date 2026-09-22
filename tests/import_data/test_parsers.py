from pathlib import Path

import pytest

from bin_tools.dataclasses.bin import Bin
from bin_tools.dataclasses.contig import Contig
from bin_tools.enums import Assembler
from bin_tools.import_data.assembly import parse_assembly_fasta
from bin_tools.import_data.binset import parse_bins

TEST_DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def assembly_file():
    """Path to the assembly FASTA file."""
    return TEST_DATA_DIR / "asm.fasta"


@pytest.fixture
def bin_files():
    """Paths to valid bin FASTA files."""
    bins_dir = TEST_DATA_DIR / "bins"
    return [bins_dir / "bin1.fasta", bins_dir / "bin2.fasta"]


@pytest.fixture
def bin_files_binsplit():
    """Paths to binsplit bin FASTA files."""
    bins_dir = TEST_DATA_DIR / "bins_binsplit"
    return [bins_dir / "bin1.fasta", bins_dir / "bin2.fasta"]


class TestParseAssemblyFasta:
    def test_parse_assembly_returns_contigs(self, assembly_file):
        """Test that parse_assembly_fasta returns a dict of Contig objects."""
        contigs = parse_assembly_fasta(assembly_file, assembler=Assembler.metamdbg)
        assert isinstance(contigs, dict)
        assert len(contigs) > 0
        assert all(isinstance(c, Contig) for c in contigs.values())

    def test_contig_attributes(self, assembly_file):
        """Test that contigs have expected attributes."""
        contigs = parse_assembly_fasta(assembly_file, assembler=Assembler.metamdbg)
        contig = next(iter(contigs.values()))
        assert hasattr(contig, "id")
        assert hasattr(contig, "sequence")
        assert hasattr(contig, "sequence_length")
        assert hasattr(contig, "topology")
        assert len(contig.sequence) == contig.sequence_length

    def test_circular_detected(self, assembly_file):
        """Test that circular topology is detected."""
        contigs = parse_assembly_fasta(assembly_file, assembler=Assembler.metamdbg)
        assert all(
            c.topology == "circular" for c in contigs.values() if c.id == "contig1"
        )

    def test_contig_sequence_uppercase(self, assembly_file):
        """Test that sequences are uppercase."""
        contigs = parse_assembly_fasta(assembly_file, assembler=Assembler.metamdbg)
        assert all(c.sequence.isupper() for c in contigs.values())

    def test_duplicate_sequence_id_raises_error(self, tmp_path):
        """Test that duplicate sequence IDs raise ValueError."""
        fasta_file = tmp_path / "dup.fasta"
        fasta_file.write_text(">seq1\nACGT\n>seq1\nTGCA\n")
        with pytest.raises(ValueError, match="Duplicate sequence id"):
            parse_assembly_fasta(fasta_file, assembler=None)


class TestParseBins:
    def test_parse_bins_returns_bins(self, bin_files):
        """Test that parse_bins returns a list of Bin objects."""
        bins = parse_bins(bin_files, group="test")
        assert isinstance(bins, list)
        assert len(bins) > 0
        assert all(isinstance(b, Bin) for b in bins)

    def test_bin_attributes(self, bin_files):
        """Test that bins have expected attributes."""
        bins = parse_bins(bin_files, group="test")
        bin_obj = bins[0]
        assert hasattr(bin_obj, "id")
        assert hasattr(bin_obj, "filename")
        assert hasattr(bin_obj, "group")
        assert hasattr(bin_obj, "contigs")
        assert bin_obj.group == "test"

    def test_bin_contigs_is_list(self, bin_files):
        """Test that bin contigs is a list of contig IDs."""
        bins = parse_bins(bin_files, group="test")
        assert all(isinstance(b.contigs, list) for b in bins)
        assert all(isinstance(cid, str) for b in bins for cid in b.contigs)

    def test_parse_bins_with_rename_prefix(self, bin_files):
        """Test parse_bins with rename_prefix parameter."""
        bins = parse_bins(bin_files, group="test", rename_prefix="custom")
        assert bins[0].id == "custom_1"
        assert bins[1].id == "custom_2"

    def test_parse_bins_default_id_is_basename(self, bin_files):
        """Test that default bin ID is the file basename."""
        bins = parse_bins(bin_files, group="test")
        assert bins[0].id == "bin1"
        assert bins[1].id == "bin2"

    def test_parse_bins_with_binsplit_separator(self, bin_files_binsplit):
        """Test parse_bins with binsplit_separator to extract contig IDs."""
        bins = parse_bins(bin_files_binsplit, group="test", binsplit_separator=":")
        assert bins[0].contigs == ["contig1"]
        assert bins[1].contigs == ["contig2"]

    def test_parse_bins_without_binsplit_separator(self, bin_files_binsplit):
        """Test parse_bins without binsplit_separator keeps full IDs."""
        bins = parse_bins(bin_files_binsplit, group="test")
        assert bins[0].contigs == ["s1:contig1"]
        assert bins[1].contigs == ["s2:contig2"]
