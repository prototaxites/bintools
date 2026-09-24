Installation
=============

From PyPI
---------

Install the latest released version:

.. code-block:: bash

   pip install bin-tools

From Source
-----------

Clone the repository and install in development mode:

.. code-block:: bash

   git clone https://github.com/yourusername/metabintools.git
   cd metabintools
   pip install -e .

Development Installation
--------------------------

If you want to contribute to metabintools, install with development dependencies:

.. code-block:: bash

   git clone https://github.com/yourusername/metabintools.git
   cd metabintools
   uv sync --all-extras --dev

Requirements
------------

- Python 3.13 or later
- Dependencies will be installed automatically:

  - click >= 8.5.0 (CLI framework)
  - loguru >= 0.7.3 (Logging)
  - pydantic >= 2.13.5 (Data validation)
  - pyfastx >= 2.3.1 (FASTA/FASTQ parsing)
  - zstandard >= 0.25.0 (Compression)

Verification
------------

Verify the installation was successful:

.. code-block:: bash

   metabintools --version
   metabintools --help
