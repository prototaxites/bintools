import gzip
import json
from pathlib import Path

import jsonschema


class BinSet:
    _schemas = {}

    def __init__(self, assembly: dict[str, str], bins: dict[str, str]):
        self._assembly = {}
        self._bins = {}

        if assembly:
            self.validate_assembly(assembly)
        if bins:
            self.validate_bins(bins)

    @property
    def assembly(self) -> dict[str, str]:
        return self._assembly

    @property
    def bins(self) -> dict[str, str]:
        return self._bins

    @property
    def binset(self) -> dict[str, dict[str, str]]:
        return {
            "assembly": self._assembly,
            "bins": self._bins,
        }

    @classmethod
    def _load_schema(cls, schema_name: str) -> dict:
        if schema_name not in cls._schemas:
            schema_path = Path(__file__).parent / "schemas" / f"{schema_name}.json"

            with open(schema_path) as f:
                cls._schemas[schema_name] = json.load(f)
        return cls._schemas[schema_name]

    def validate_assembly(self, assembly: dict[str, str]) -> None:
        schema = self._load_schema("assembly_schema")
        jsonschema.validate(assembly, schema)
        self._assembly = assembly

    def validate_bins(self, bins: dict[str, str]) -> None:
        schema = self._load_schema("bin_schema")
        jsonschema.validate(bins, schema)
        self._bins = bins

    def write(self, output_path: Path) -> None:
        with gzip.open(output_path, "wt") as f:
            json.dump(self.binset, f)
