"""
Filter module for filtering bins in a BinSet.
"""

from bin_tools.dataclasses.binset import BinSet
from bin_tools.filter.query_parser import parse_filter_query


def filter_binset(binset: BinSet, query: str) -> BinSet:
    """
    Filter a BinSet based on a query expression.

    Args:
        binset: The BinSet to filter
        query: Filter query expression (e.g., "completeness >= 0.9 and contamination <= 0.05")

    Returns:
        A new BinSet containing only bins that match the filter

    Raises:
        ValueError: If the query is invalid
    """
    if binset.bins is None:
        return binset.model_copy(update={"bins": None})

    filter_func = parse_filter_query(query)

    filtered_bins = [bin for bin in binset.bins if filter_func(bin)]

    return binset.model_copy(update={"bins": filtered_bins})
