from pathlib import Path
import json, jsonschema

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"


def load_schema(name: str) -> dict:
    with open(SCHEMA_DIR / name) as f:
        return json.load(f)


def validate_payload(schema_name: str, data: dict):
    schema = load_schema(schema_name)
    jsonschema.validate(data, schema)
    return True
