bintools Documentation
======================

A toolkit for managing and manipulating metagenomic binning outputs.

**bintools** consolidates metagenomic bin data, including sequences, annotations, quality metrics, and taxonomy, into a single unified file format for streamlined analysis workflows.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quick_start
   file_format

.. toctree::
   :maxdepth: 2
   :caption: Reference

   cli_reference
   api_reference

Key Features
============

- **Unified file format**: Store bins, contigs, annotations, quality scores, and taxonomy in one ``.bins`` file
- **Composable operations**: Chain commands via Unix pipes for flexible workflows
- **Powerful filtering**: Query bins by any property (completeness, contamination, taxonomy, etc.)
- **Compression support**: Optional zstd compression for efficient storage
- **Multiple input sources**: Import bin metadata from many metagenomics tools (CheckM, GTDB-Tk, etc.)

Quick Links
===========

- `GitHub Repository <https://github.com/prototaxites/bintools>`_
- `PyPI Package <https://pypi.org/project/bin-tools>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
