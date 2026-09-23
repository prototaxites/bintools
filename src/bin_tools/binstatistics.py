from bin_tools.dataclasses.contig import Contig


class CalculateBinStatistics:
    @staticmethod
    def bin_size(contig_dict: dict[str, Contig]) -> int:
        """Calculate the total size of the bin."""
        return sum(contig.sequence_length for contig in contig_dict.values())

    @staticmethod
    def bin_n50(contig_dict: dict[str, Contig]) -> int:
        """Calculate the N50 of the bin."""
        lengths = [contig.sequence_length for contig in contig_dict.values()]
        lengths.sort(reverse=True)
        total = sum(lengths)
        half = total // 2
        for length in lengths:
            if total >= half:
                return length
            total -= length
        return 0

    @staticmethod
    def bin_longest_contig(contig_dict: dict[str, Contig]) -> int:
        """Calculate the length of the longest contig in the bin."""
        return max(contig.sequence_length for contig in contig_dict.values())

    @staticmethod
    def bin_n_circular(contig_dict: dict[str, Contig]) -> int:
        """Calculate the number of circular contigs in the bin."""
        return sum(
            1 for contig in contig_dict.values() if contig.topology == "circular"
        )

    @staticmethod
    def bin_n_unique_trnas(contig_dict: dict[str, Contig]) -> int:
        """Extract unique tRNA products from the bin."""
        trnas = [
            trna for contig in contig_dict.values() for trna in (contig.trnas or [])
        ]
        return len(list(set(trnas)))

    @staticmethod
    def bin_has_5s(contig_dict: dict[str, Contig]) -> bool:
        """Check if the bin contains 5S rRNA."""
        return any(contig.has_5s for contig in contig_dict.values())

    @staticmethod
    def bin_has_16s(contig_dict: dict[str, Contig]) -> bool:
        """Check if the bin contains 16S rRNA."""
        return any(contig.has_16s for contig in contig_dict.values())

    @staticmethod
    def bin_has_23s(contig_dict: dict[str, Contig]) -> bool:
        """Check if the bin contains 23S rRNA."""
        return any(contig.has_23s for contig in contig_dict.values())

    @staticmethod
    def bin_coverage(contig_dict: dict[str, Contig]) -> float | None:
        """Calculate the average coverage of the bin."""
        coverages = [
            contig.coverage
            for contig in contig_dict.values()
            if contig.coverage is not None
        ]
        if len(coverages) == len(contig_dict):
            return sum(coverages) / len(coverages)
        return None
