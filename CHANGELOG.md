# metabintools: changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [[0.2.1](https://github.com/sanger-tol/metabintools/releases/tag/0.2.1)] - [2026-09-24]

- Read the isotype field of a tRNA annotation to get the gene, enabling compatibility with tRNAScan-SE

## [[0.2.0](https://github.com/sanger-tol/metabintools/releases/tag/0.2.0)] - [2026-09-24]

- Rename package to metabintools to avoid PyPi conflicts.
- Add `metabintools summarise groups` command which prints an aggregated TSV summary of MiMAG counts for each bin group.
- If importing NCBI taxonomy, now tries to find and set a submittable taxonomic name and taxID by querying ENA.

## [[0.1.0](https://github.com/sanger-tol/metabintools/releases/tag/v0.1.0)] - [2026-09-23]

Base release of metabintools.
