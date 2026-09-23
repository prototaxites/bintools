API Reference
=============

This page provides detailed documentation of the metabintools Python API for programmatic use.

Core Data Structures
====================

BinSet
------

.. autoclass:: bin_tools.dataclasses.binset.BinSet
   :members:
   :undoc-members:
   :show-inheritance:

The main class representing a collection of contigs and bins.

Bin
---

.. autoclass:: bin_tools.dataclasses.bin.Bin
   :members:
   :undoc-members:
   :show-inheritance:

Represents a single metagenomic bin with statistics and taxonomy.

BinStatistics
-------------

.. autoclass:: bin_tools.dataclasses.bin.BinStatistics
   :members:
   :undoc-members:
   :show-inheritance:

Statistics computed for a bin.

BinTaxonomy
-----------

.. autoclass:: bin_tools.dataclasses.bin.BinTaxonomy
   :members:
   :undoc-members:
   :show-inheritance:

Taxonomy information for a bin.

Contig
------

.. autoclass:: bin_tools.dataclasses.contig.Contig
   :members:
   :undoc-members:
   :show-inheritance:

Represents a single contig sequence.

Annotation
----------

.. autoclass:: bin_tools.dataclasses.annotation.Annotation
   :members:
   :undoc-members:
   :show-inheritance:

GFF-format annotation for a contig.

Import Functions
================

Assembly Parsing
----------------

.. automodule:: bin_tools.import_data.assembly
   :members:
   :undoc-members:

Bin Parsing
-----------

.. automodule:: bin_tools.import_data.binset
   :members:
   :undoc-members:

Annotation Processing
---------------------

.. automodule:: bin_tools.import_data.annotation
   :members:
   :undoc-members:

Coverage Data
-------------

.. automodule:: bin_tools.import_data.coverage
   :members:
   :undoc-members:

Quality Scores
--------------

.. automodule:: bin_tools.import_data.quality
   :members:
   :undoc-members:

Taxonomy
--------

.. automodule:: bin_tools.import_data.taxonomy
   :members:
   :undoc-members:

Export Functions
================

.. autoclass:: bin_tools.export.binset_exporter.BinSetExporter
   :members:
   :undoc-members:

Query and Filtering
===================

.. automodule:: bin_tools.query.query_parser
   :members:
   :undoc-members:

Operations
==========

Merging
-------

.. automodule:: bin_tools.operations.merge
   :members:
   :undoc-members:

Renaming
--------

.. automodule:: bin_tools.operations.rename
   :members:
   :undoc-members:

Enumerations
============

.. automodule:: bin_tools.enums
   :members:
   :undoc-members:

Utilities
=========

Bin Statistics Calculation
---------------------------

.. automodule:: bin_tools.binstatistics
   :members:
   :undoc-members:

File Utilities
--------------

.. automodule:: bin_tools.bin_utils
   :members:
   :undoc-members:

Example Usage
=============

Programmatic Workflow
---------------------

Here's an example of using metabintools as a Python library:

.. code-block:: python

   from pathlib import Path
   from bin_tools.dataclasses.binset import BinSet
   from bin_tools.import_data.assembly import parse_assembly_fasta
   from bin_tools.import_data.binset import parse_fasta_bins
   from bin_tools.enums import Assembler

   # Load assembly
   assembly_path = Path("metagenome.fasta")
   contigs = parse_assembly_fasta(assembly_path, Assembler.metamdbg)

   # Load bins
   bin_paths = [Path("bins/bin1.fa"), Path("bins/bin2.fa")]
   bins = parse_fasta_bins(bin_paths, group="metabat", asm_contigs=contigs)

   # Create BinSet
   binset = BinSet(contigs=contigs, bins=bins)

   # Filter bins
   filtered = binset.filter_bins("completeness >= 0.9")

   # Export to FASTA
   from bin_tools.export.binset_exporter import BinSetExporter
   exporter = BinSetExporter(filtered)
   exporter.export_fasta(Path("output/"), compress=False)

Reading and Writing BinFiles
-----------------------------

.. code-block:: python

   from bin_tools.dataclasses.binset import BinSet
   from bin_tools.export.binset_exporter import BinSetExporter

   # Read a binfile
   with open("project.bins", "rb") as f:
       binset = BinSet.read_binfile(f)

   # Perform operations
   filtered = binset.filter_bins("tax_phylum == 'Bacteroidetes'")

   # Write back (optionally compressed)
   with open("output.bins.zstd", "wb") as f:
       exporter = BinSetExporter(filtered)
       exporter.write_binfile(f, compress=True)
