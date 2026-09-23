# bintools

**bintools** is a toolkit for managing and manipulating metagenomic binning outputs. It consolidates all bin data, including sequences, annotations, quality metrics, and taxonomy, into a single unified file format for streamlined analysis workflows. This file can be queried, filtered, bins can be renamed using their metadata, and separate files can easily be merged to consolidate bins into a single file.

## Overview

Metagenomic binning produces scattered outputs: bin FASTA files, quality assessments, taxonomic classifications, and annotations in separate formats. **bintools** unifies these into a single `.bins` file (optionally compressed as `.bins.zstd`), enabling easy filtering, merging, and export via composable command-line operations.

## Key Features

- **Unified file format**: Store bins, contigs, annotations, quality scores, and taxonomy in one `.bins` file
- **Composable operations**: Chain commands via Unix pipes for flexible workflows
- **Powerful filtering**: Query bins by any property (completeness, contamination, taxonomy, etc.)
- **Compression support**: Optional zstd compression for efficient storage
- **Multiple input sources**: Import bin metadata from many metagenomics tools (CheckM, GTDB-Tk, etc.)

## Installation

```bash
pip install bin-tools ## not on pip yet!
```

## Quick Start

### 1. Create a binfile from your assembly

```bash
bintools import asm assembly.fasta -o binset.bins
```

### 2. Add annotations to your binfile

```bash
bintools import annotations binset.bins annotations.gff -o binset.bins
```

### 3. Add bins from your binner

```bash
bintools import binset binset.bins bins/ --group "myBinner" -o binset.bins
```

### 4. Add quality scores

```bash
bintools import quality binset.bins checkm_results.tsv --tool checkm -o binset.bins
```

### 5. Add taxonomy

```bash
bintools import taxonomy binset.bins gtdbtk.tsv --tool gtdbtk -o binset.bins
```

### 6. Filter high-quality bins

```bash
bintools filter binset.bins 'completeness >= 0.9 and contamination <= 0.05' -o hq.bins
```

or, if the required data for MiMAG calls is present (completeness, contamination, tRNAs, rRNAs):

```bash
bintools filter binset.bins 'mimag == "high"' -o hq.bins
```

### 7. Export to FASTA

```bash
bintools export fasta hq.bins -o output_directory/
```

## Composable Workflows

The real power of bintools is composability via piping:

```bash
# Filter and export in one pipeline
bintools filter binset.bins 'group == "metabat" and completeness >= 0.8' -z | \
  bintools export fasta -o filtered_bins/

# Merge multiple binsets and filter
bintools merge set1.bins.zstd set2.bins.zstd -z | \
  bintools filter - 'contamination <= 0.1' -o merged_hq.bins.zstd

# Extract high-quality archaeal bins
bintools filter binset.bins 'tax_kingdom == "Archaea" and completeness >= 0.85' -o archaea_hq.bins
```

## Filter Query Guide

The `filter` command uses simple Python-like syntax:

```bash
# Basic comparisons
bintools filter input.bins 'completeness >= 0.9' -o output.bins
bintools filter input.bins 'length > 1000000' -o output.bins

# Logical operators
bintools filter input.bins 'completeness >= 0.9 and contamination <= 0.05' -o output.bins
bintools filter input.bins 'group == "vamb" or group == "metabat"' -o output.bins

# Taxonomy filtering
bintools filter input.bins 'tax_phylum == "Bacteroidetes"' -o output.bins

# Complex queries
bintools filter input.bins 'group == "archaea" and completeness >= 0.8 and contamination <= 0.1' -o output.bins
```

### Available Filter Fields

List all available fields:

```bash
bintools filter --list-fields
```

## Commands

### import

Import data into a binfile with validation and error handling:

- **`bintools import asm`** - Initialize from assembly FASTA
  - Handles gzip-compressed assemblies automatically
  - Validates input format with clear error messages
  - Supports standard and custom assembler metadata

- **`bintools import binset`** - Add contig clusters from binning
  - Accepts bin FASTA files or directories of bin files
  - Validates file integrity before import
  - Optional binsplit separator recovery (SemiBin2, VAMB compatibility)
  - Custom bin rename prefix support

- **`bintools import annotation`** - Add GFF annotations to contigs
  - Validates GFF format and contig references
  - Option to overwrite existing annotations
  - Informative error messages for format issues

- **`bintools import coverage`** - Add coverage data to contigs
  - Supports multiple coverage tools (e.g., CoverM, custom formats)
  - Validates coverage values and contig references
  - Automatic statistics recalculation

- **`bintools import taxonomy`** - Add taxonomic classifications to bins
  - Supports multiple taxonomy tools (GTDB-Tk, DIAMOND, manual)
  - Validates bin references and taxonomy format
  - Informative errors for missing or malformed data

- **`bintools import quality`** - Add quality scores (CheckM, CheckM2, BUSCO) to bins
  - Supports multiple quality assessment tools
  - Validates score ranges and bin references
  - Automatic statistics recalculation

### filter

Filter bins by query expression with comprehensive validation:

```bash
bintools filter input.bins 'completeness >= 0.9' -o output.bins
bintools filter input.bins 'completeness >= 0.9' -z -o output.bins.zstd  # compressed
bintools filter --list-fields  # Show all available filter fields
```

Features:
- Validates query syntax before processing (informative parse errors)
- Progress reporting (bins read, bins matched, bins written)
- Shows matching bin counts before/after filtering
- Comprehensive error handling for file I/O issues

### export

Export data from a binfile:

- **`bintools export fasta`** - Export each bin to a FASTA file

- **`bintools export gff`** - Export each bin's annotations to a GFF file

- **`bintools export contig2bin`** - Export a set of bins to a contig-to-bin mapping (DAS_Tool format)

### merge

Combine multiple binfiles with progress tracking and validation:

```bash
bintools merge set1.bins set2.bins set3.bins -o merged.bins
```

### trim

Remove unused contigs from a binfile:

```bash
bintools trim input.bins -o trimmed.bins
```

### rename

Rename bins in a binfile with template support. Field options can be listed with `--list-fields`.

```bash
bintools rename input.bins -n "bin_{tax_phylum}" -o output.bins
# bin1, bin2 > bin_Pseudomonadota_1, bin_Pseudomonadota_2
```

### summarise

Generate summary reports:

- **`bintools summarise bins`** - Export bin summary to TSV
- **`bintools summarise contigs`** - Export contig summary to TSV

## File Format

A `.bins` file is a zstd-compressed (or uncompressed) JSON document containing:

```json
{
  "contigs": {
    "contig_id": {
      "id": "contig_id",
      "sequence": "ACGTACGT...",
      "sequence_length": 1234,
      "annotations": [...],
      "coverage": 15.5,
      "topology": "circular"
    }
  },
  "bins": [
    {
      "id": "bin.1",
      "group": "metabat",
      "contigs": ["contig_1", "contig_2"],
      "statistics": {
        "completeness": 0.95,
        "contamination": 0.02,
        "length": 2500000
      },
      "taxonomy": {
        "classification": "k__Bacteria;p__Proteobacteria;..."
      }
    }
  ]
}
```

## Examples

### Workflow: Filter and Export High-Quality Bins

```bash
# Start with assembly
bintools import asm metagenome.fasta -o project.bins

# Add binning results
bintools import binset project.bins bins/ --group "metabat" -o project.bins

# Add quality scores
bintools import quality project.bins checkm_results.tsv --tool checkm -o project.bins

# Add taxonomy
bintools import taxonomy project.bins gtdbtk.tsv --tool gtdbtk -o project.bins

# Filter to high-quality bins
bintools filter project.bins 'completeness >= 0.9 and contamination <= 0.05' \
  -o high_quality.bins

# Export to FASTA
bintools export fasta high_quality.bins -o bins_fasta/
```

## License

MIT © 2026 Genome Research Ltd
