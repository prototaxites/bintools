"""Bin renaming operations."""

import re

from loguru import logger

from metabintools.dataclasses.bin import Bin
from metabintools.query.query_parser import parse_rename_template


def rename_bins(bins: list[Bin], template: str) -> list[Bin]:
    """Rename bins using a template with field name injection.

    Template placeholders are replaced with bin field values. If multiple bins
    end up with the same name, numeric suffixes are appended (_1, _2, etc.).

    Args:
        bins: List of bins to rename
        template: A template string with field placeholders like "bin_{taxon_name}"
                 Available placeholders: id, group, completeness, contamination,
                 phylum, taxon_name, and other bin/statistics/taxonomy fields.

    Returns:
        A list of renamed bins

    Raises:
        ValueError: If the template contains invalid field references

    Examples:
        renamed = rename_bins(bins, "bin_{taxon_name}")
        # Returns bins renamed to: bin_Bacteroides sp., bin_Firmicutes sp., etc.

        renamed = rename_bins(bins, "bin_{group}_{id}")
        # Returns bins renamed with group and original id
    """
    rename_func = parse_rename_template(template)

    # Generate new names and handle collisions
    name_counts: dict[str, int] = {}
    renamed_bins = []

    for bin in bins:
        new_name = rename_func(bin)

        if new_name not in name_counts:
            name_counts[new_name] = 1
        else:
            name_counts[new_name] += 1

        new_name = f"{new_name}_{name_counts[new_name]}"
        new_name = re.sub(r"\s+", "_", new_name)
        logger.info(f"Renaming bin {bin.id} to {new_name}")

        renamed_bin = bin.model_copy(update={"id": new_name})
        renamed_bins.append(renamed_bin)

    return renamed_bins
