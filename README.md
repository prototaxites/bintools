# bintools README

A toolkit for managing and manipulating metagenomic binning outputs. **bintools** consolidates all bin data - sequences, annotations, quality metrics, and taxonomy - into a single unified file format for streamlined analysis workflows.

## Overview

Metagenomic binning produces scattered outputs: bin FASTA files, quality assessments, taxonomic classifications, and annotations in separate formats. **bintools** unifies these into a single `.bins` file (optionally compressed as `.bins.zstd`), enabling easy filtering, merging, and export via composable command-line operations.

## Key Features

- **Unified file format**: Store bins, contigs, annotations, quality scores, and taxonomy in one `.bins` file
- **Composable operations**: Chain commands via Unix pipes for flexible workflows
- **Powerful filtering**: Query bins by any property (completeness, contamination, taxonomy, etc.)
- **Compression support**: Optional zstd compression for efficient storage
- **Multiple input sources**: Import from standard binning tools (CheckM, GTDB-Tk, etc.)

## Installation

```bash
pip install bin-tools
```

## Quick Start

### 1. Create a binfile from your assembly

```bash
bintools import asm assembly.fasta -o binset.bins
```

### 2. Add bins from your binner

```bash
bintools import binset binset.bins bins/ --group "myBinner" -o binset.bins
```

### 3. Add quality scores

```bash
bintools import quality binset.bins checkm_results.tsv --tool checkm -o binset.bins
```

### 4. Add taxonomy

```bash
bintools import taxonomy binset.bins gtdbtk.tsv --tool gtdbtk -o binset.bins
```

### 5. Filter high-quality bins

```bash
bintools filter binset.bins 'completeness >= 0.9 and contamination <= 0.05' -o hq.bins
```

### 6. Export to FASTA

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

Common fields include:
- **Bin properties**: `id`, `group`, `import_name`, `n_contigs`
- **Statistics**: `completeness`, `contamination`, `length`, `coverage`, `longest`, `n50`
- **Taxonomy**: `tax_kingdom`, `tax_phylum`, `tax_class`, `tax_order`, `tax_family`, `tax_genus`, `tax_species`

## Commands

### import

Import data into a binfile:

- `bintools import asm` - Initialize from assembly FASTA
- `bintools import binset` - Add contig clusters from binning
- `bintools import annotation` - Add GFF annotations to contigs
- `bintools import coverage` - Add coverage data to contigs
- `bintools import taxonomy` - Add taxonomic classifications to bins
- `bintools import quality` - Add quality scores (CheckM, CheckM2, BUSCO) to bins

### filter

Filter bins by query expression:

```bash
bintools filter input.bins 'completeness >= 0.9' -o output.bins
bintools filter input.bins 'completeness >= 0.9' -z -o output.bins.zstd  # compressed
```

### export

Export data from a binfile:

- `bintools export fasta` - Export bin sequences as FASTA
- `bintools export gff` - Export annotations as GFF
- `bintools export contig2bin` - Export contig-to-bin mapping (DAS_Tool format)

### merge

Combine multiple binfiles:

```bash
bintools merge set1.bins set2.bins set3.bins -o merged.bins
```

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

### Workflow: Compare Multiple Binning Runs

```bash
# Create separate binfiles for each binner
bintools import asm assembly.fasta -o metabat.bins
bintools import binset metabat.bins metabat_output/ --group "metabat" -o metabat.bins

bintools import asm assembly.fasta -o vamb.bins
bintools import binset vamb.bins vamb_output/ --group "vamb" -o vamb.bins

# Merge and compare
bintools merge metabat.bins vamb.bins -o combined.bins

# Export each binner's bins separately
bintools filter combined.bins 'group == "metabat"' -o metabat_filtered.bins
bintools export fasta metabat_filtered.bins -o metabat_export/

bintools filter combined.bins 'group == "vamb"' -o vamb_filtered.bins
bintools export fasta vamb_filtered.bins -o vamb_export/
```

## License

MIT © 2026 Genome Research Ltd
