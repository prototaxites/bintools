from pathlib import Path

import pytest
from pydantic import ValidationError

from bin_tools.dataclasses.binset import BinSet
from bin_tools.enums import Assembler
from bin_tools.import_data.assembly import parse_assembly_fasta
from bin_tools.import_data.binset import parse_bins

TEST_DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def data_assembly():
    """Fixture that loads the assembly from tests/data/asm.fasta."""
    assembly_file = TEST_DATA_DIR / "asm.fasta"
    return parse_assembly_fasta(assembly_file, assembler=Assembler.metamdbg)


@pytest.fixture
def data_bins_valid():
    """Fixture that loads valid bins from tests/data/bins/."""
    bins_dir = TEST_DATA_DIR / "bins"
    return parse_bins([bins_dir / "bin1.fasta", bins_dir / "bin2.fasta"], group="test")


@pytest.fixture
def data_bins_invalid():
    """Fixture that loads invalid bins from tests/data/incorrect_bins/."""
    bins_dir = TEST_DATA_DIR / "incorrect_bins"
    return parse_bins([bins_dir / "bin1.fasta", bins_dir / "bin2.fasta"], group="test")


class TestBinSet:
    def test_validation_valid_bins(self, data_assembly, data_bins_valid):
        try:
            binset = BinSet(contigs=data_assembly, bins=data_bins_valid)
            BinSet.model_validate(binset)
        except ValidationError:
            pytest.fail("Validation should pass for correct binset")

    def test_validation_invalid_bins(self, data_assembly, data_bins_invalid):
        with pytest.raises(ValidationError):
            binset = BinSet(contigs=data_assembly, bins=data_bins_invalid)
            BinSet.model_validate(binset)

    def test_write_binset_uncompressed(self, data_assembly, data_bins_valid, tmp_path):
        outfile = tmp_path / "binset.json"
        binset = BinSet(contigs=data_assembly, bins=data_bins_valid)

        with open(outfile, "wb") as f:
            binset.write(f)

        assert outfile.exists()

        with open(outfile, "rb") as f:
            data = f.read()

        assert data[:4] != b"\x28\xb5\x2f\xfd", "Output is zstd compressed"

    def test_write_binset_compressed(self, data_assembly, data_bins_valid, tmp_path):
        outfile = tmp_path / "binset.json"
        binset = BinSet(contigs=data_assembly, bins=data_bins_valid)

        with open(outfile, "wb") as f:
            binset.write(f, compress=True)

        assert outfile.exists()

        with open(outfile, "rb") as f:
            data = f.read()

        assert data[:4] == b"\x28\xb5\x2f\xfd", "Output is not zstd compressed"
