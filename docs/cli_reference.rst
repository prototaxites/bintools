CLI Reference
==============

This page documents the complete command-line interface for bintools.

All commands support reading from stdin (``-``) and writing to stdout (``-``), enabling Unix pipes.
Commands support compression with the ``-z`` flag, and the format is auto-detected on input.

Import Commands
===============

The ``import`` group contains commands for adding data to a binfile.

import asm
----------

Import a metagenomic assembly to initialize a binfile.

.. code-block:: bash

   bintools import asm ASSEMBLY [OPTIONS]

Arguments:

- ``ASSEMBLY``: Input FASTA file (required; path to file)

Options:

- ``--assembler {spades,megahit,flye,metamdbg,myloasm,hifiasm_meta}``: Assembler used to generate the assembly (optional)
- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Features:

- Automatically detects circular contigs from assembler-specific headers
- Supports gzip-compressed FASTA files
- Validates sequence content

Example:

.. code-block:: bash

   bintools import asm assembly.fasta --assembler metamdbg -o project.bins

import binset
-------------

Add bins from binning tool output.

.. code-block:: bash

   bintools import binset BINFILE FASTA [FASTA ...] --group NAME [OPTIONS]

Arguments:

- ``BINFILE``: Existing binfile to add bins to (use ``-`` for stdin)
- ``FASTA``: Bin FASTA files or directories containing them

Options:

- ``--group NAME``: Name for this bin group (required)
- ``--binsplit-separator SEP``: Separator for recovering contig names (e.g., ":" for VAMB/SemiBin2)
- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Example:

.. code-block:: bash

   bintools import binset project.bins bins/ --group "metabat" -o project.bins

import annotation
-----------------

Add GFF3 annotations to contigs.

.. code-block:: bash

   bintools import annotation BINFILE GFF [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to annotate (use ``-`` for stdin)
- ``GFF``: GFF3 annotation file (path to file)

Options:

- ``--overwrite``: Overwrite existing annotations (flag, default: false)
- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Example:

.. code-block:: bash

   bintools import annotation project.bins annotations.gff -o project.bins

import coverage
---------------

Add coverage data to contigs.

.. code-block:: bash

   bintools import coverage BINFILE COVERAGE [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to add coverage to (use ``-`` for stdin)
- ``COVERAGE``: Coverage file from Metabat2's jgi_summarize_bam_depths script

Options:

- ``--tool {metabat}``: Tool that generated the coverage file (default: metabat)
- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Example:

.. code-block:: bash

   bintools import coverage project.bins coverage.tsv --tool metabat -o project.bins

import quality
---------------

Add quality scores from binning assessment tools.

.. code-block:: bash

   bintools import quality BINFILE --quality FILE --tool TOOL [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to add quality to (use ``-`` for stdin)

Options:

- ``--quality FILE``: Quality assessment file (required)
- ``--tool {checkm,checkm2,busco,manual}``: QC tool used (default: manual)
- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Notes:

- For CheckM, CheckM2, and BUSCO: use output files directly
- For manual TSV: must have fields ``File``, ``Completeness``, and ``Contamination``

Example:

.. code-block:: bash

   bintools import quality project.bins --quality checkm2.tsv --tool checkm2 -o project.bins

import taxonomy
----------------

Add taxonomic classifications to bins.

.. code-block:: bash

   bintools import taxonomy BINFILE --taxonomy FILE --tool TOOL [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to add taxonomy to (use ``-`` for stdin)

Options:

- ``--taxonomy FILE``: Taxonomy file (required)
- ``--tool {gtdbtk,gtdbtk_ncbi,manual}``: Taxonomy tool used (default: manual)
- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Notes:

- For GTDB-Tk: use the ar122_summary.tsv or bac120_summary.tsv files
- For GTDB-Tk NCBI: use output from gtdb_to_ncbi_majority_vote.py script
- For manual TSV: must have fields ``File`` and ``Classification`` (lineage string format: k__.*;p__.*...)

Example:

.. code-block:: bash

   bintools import taxonomy project.bins --taxonomy gtdbtk.tsv --tool gtdbtk -o project.bins

Export Commands
===============

The ``export`` group contains commands for extracting data from binfiles.

export fasta
------------

Export bins to individual FASTA files.

.. code-block:: bash

   bintools export fasta BINFILE --outdir DIR [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to export (use ``-`` for stdin)

Options:

- ``--outdir, -o``: Output directory (required)
- ``--compress, -z``: Compress output FASTA files with gzip
- ``--preserve-headers, -h``: Keep original FASTA headers
- ``--group-fasta, -g``: Create subdirectories for each bin group

Example:

.. code-block:: bash

   bintools export fasta project.bins -o bins/ --group-fasta

export gff
----------

Export bin annotations to GFF3 files.

.. code-block:: bash

   bintools export gff BINFILE --outdir DIR [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to export

Options:

- ``--outdir, -o``: Output directory (required)
- ``--group-gff, -g``: Create subdirectories for each bin group

Example:

.. code-block:: bash

   bintools export gff project.bins -o annotations/

export contig2bin
------------------

Export contig-to-bin mapping in DAS_Tool format.

.. code-block:: bash

   bintools export contig2bin BINFILE --output FILE [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to export (use ``-`` for stdin)

Options:

- ``--output, -o``: Output file path (required)
- ``--group, -g``: Export only bins from a specific group (optional)

Example:

.. code-block:: bash

   bintools export contig2bin project.bins -o contig2bin.tsv

   # Export only a specific group
   bintools export contig2bin project.bins -o contig2bin.tsv --group metabat

View Command
==============

Filter bins from a binfile based on a query expression.

.. code-block:: bash

   bintools view BINFILE [QUERY] [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to filter (use ``-`` for stdin)
- ``QUERY``: Filter expression (optional; if omitted, all bins are included)

Options:

- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)
- ``--list-fields``: Show all available filter fields and exit

Examples:

.. code-block:: bash

   # Filter by quality
   bintools view project.bins 'completeness >= 0.9' -o hq.bins

   # Filter by multiple criteria
   bintools view project.bins 'completeness >= 0.9 and contamination <= 0.05' -o hq.bins

   # Filter by taxonomy
   bintools view project.bins 'phylum == "Bacteroidetes"' -o output.bins

   # Filter by group
   bintools view project.bins 'group == "metabat"' -o output.bins

   # List available fields
   bintools view --list-fields

Available filter fields (see ``--list-fields`` for complete list):

- **id**: Bin identifier
- **group**: Bin group name
- **length**: Total bin size in bp
- **n_contigs**: Number of contigs
- **n_circular**: Number of circular contigs
- **completeness**: Completeness estimate (0.0-1.0)
- **contamination**: Contamination estimate (0.0-1.0)
- **coverage**: Average coverage
- **mimag**: MiMAG quality level (high, medium, low)
- **kingdom, phylum, class, order, family, genus, species**: Taxonomy fields

Merge Command
=============

Combine multiple binfiles into one.

.. code-block:: bash

   bintools merge BINFILES [BINFILES ...] [OPTIONS]

Arguments:

- ``BINFILES``: Binfiles to merge

Options:

- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Example:

.. code-block:: bash

   bintools merge set1.bins set2.bins set3.bins -o merged.bins

Trim Command
============

Remove contigs not referenced by any bin.

.. code-block:: bash

   bintools trim BINFILE [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to trim

Options:

- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Example:

.. code-block:: bash

   bintools trim project.bins -o trimmed.bins

Rename Command
==============

Rename bins using a template with field injection.

.. code-block:: bash

   bintools rename BINFILE --bin-name TEMPLATE [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to rename bins in (use ``-`` for stdin)

Options:

- ``--bin-name, -n``: Rename template with field placeholders (required)
- ``--list-fields``: Show available fields for templates
- ``--compress, -z``: Compress output with zstd
- ``--output, -o``: Output binfile path (default: stdout)

Templates use field names in curly braces. Available fields can be listed with ``--list-fields``:

.. code-block:: bash

   bintools rename project.bins -n "bin_{tax_phylum}_{completeness}" -o renamed.bins

If multiple bins end up with the same name, numeric suffixes are added (_1, _2, etc.).

Summarise Commands
==================

Generate summary reports from binfiles.

summarise bins
--------------

Create a TSV summary of bins in a binfile.

.. code-block:: bash

   bintools summarise bins BINFILE --output FILE [OPTIONS]

Arguments:

- ``BINFILE``: Binfile to summarise (use ``-`` for stdin)

Options:

- ``--output, -o``: Output TSV file path (required)
- ``--include-statistics, -s``: Include computed statistics (default: true)
- ``--include-taxonomy, -t``: Include taxonomy information (default: true)

Example:

.. code-block:: bash

   bintools summarise bins project.bins -o bin_summary.tsv

summarise contigs
------------------

Create a TSV summary of contigs in a binfile.

.. code-block:: bash

   bintools summarise contigs BINFILE --output FILE

Arguments:

- ``BINFILE``: Binfile to summarise (use ``-`` for stdin)

Options:

- ``--output, -o``: Output TSV file path (required)

Example:

.. code-block:: bash

   bintools summarise contigs project.bins -o contig_summary.tsv
