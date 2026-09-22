import sys
from pathlib import Path
from typing import IO

import zstandard as zstd
from loguru import logger
from pydantic import BaseModel, field_validator

from bintools.dataclasses.bin import Bin
from bintools.dataclasses.contig import Contig


class BinSet(BaseModel):
    contigs: dict[str, Contig]
    bins: list[Bin] | None

    @property
    def bin_contig_ids(self) -> set[str]:
        """Get the set of all contig IDs in the bins."""
        if self.bins is None:
            return set()
        return {contig_id for bin in self.bins for contig_id in bin.contigs}

    @property
    def assembly_contig_ids(self) -> set[str]:
        """Get the set of all contig IDs in the assembly."""
        return {contig for contig in self.contigs}

    @field_validator("bins")
    def validate_bin_contigs(cls, bins, info):
        """Validate that all bin contigs are present in the assembly."""
        assembly_ids = {c for c in info.data["contigs"]}
        if bins:
            for bin in bins:
                missing = set(bin.contigs) - assembly_ids
                if missing:
                    raise ValueError(
                        f"Bin {bin.id} references missing contigs: {missing}"
                    )
        return bins

    @classmethod
    def read(cls, file: IO) -> "BinSet":
        """
        Read a BinSet from a binary stream, automatically detecting zstd compression.

        Args:
            file: Binary input stream (file-like object)

        Returns:
            BinSet instance

        Raises:
            ValueError: If the data is invalid or decompression fails
        """
        data = file.read()

        try:
            dctx = zstd.ZstdDecompressor()
            json_bytes = dctx.decompress(data)
        except zstd.ZstdError:
            json_bytes = data

        json_str = json_bytes.decode()
        return cls.model_validate_json(json_str)

    def write_binfile(self, file: IO, compress: bool = False, level: int = 3):
        """
        Write the BinSet to a binary stream, optionally compressing it with zstd.

        Args:
            file: Binary output stream (file-like object)
            compress: Whether to compress the output
            level: Compression level (default: 3)
        """
        json_str = self.model_dump_json()
        json_bytes = json_str.encode()

        if compress:
            cctx = zstd.ZstdCompressor(level=level)
            compressed_data = cctx.compress(json_bytes)
            file.write(compressed_data)
        else:
            file.write(json_bytes)

    def export_fasta(
        self,
        outdir: Path,
        compress: bool,
        preserve_headers: bool = False,
        group_fasta: bool = False,
    ):
        """
        Export FASTA files for each bin in the BinSet.

        Args:
            outdir: Directory to save FASTA files
            compress: Whether to compress the output
            preserve_headers: Whether to preserve FASTA headers
        """
        if self.bins is None:
            logger.error("No bins to export.")
            sys.exit(1)
        for bin in self.bins:
            logger.info(f"Exporting FASTA for bin {bin.id}.")
            export_path = outdir
            if group_fasta:
                export_path = outdir / bin.group
                if not export_path.exists():
                    export_path.mkdir(parents=True, exist_ok=True)

            bin.export_fasta(self.contigs, export_path, compress, preserve_headers)

    def export_gff(self, outdir: Path, group_gff: bool):
        """
        Export GFF files for each bin in the BinSet.

        Args:
            outdir: Directory to save FASTA files
        """
        if self.bins is None:
            logger.error("No bins to export.")
            sys.exit(1)
        for bin in self.bins:
            logger.info(f"Exporting GFF for bin {bin.id}.")
            export_path = outdir
            if group_gff:
                export_path = outdir / bin.group
                if not export_path.exists():
                    export_path.mkdir(parents=True, exist_ok=True)

            bin.export_gff(self.contigs, export_path)

    def export_contig2bin(self, path: Path, group: str | None):
        """
        Export a contig-to-bin mapping file in DAS_Tool format.

        Args:
            path: Path to save the contig-to-bin mapping
        """
        if self.bins is None:
            logger.error("No bins to export.")
            sys.exit(1)

        with open(path, "w") as f:
            for bin in self.bins:
                if group is None or group == bin.group:
                    contigs = bin.contigs
                    f.writelines(f"{contig}\t{bin.id}\n" for contig in contigs)
