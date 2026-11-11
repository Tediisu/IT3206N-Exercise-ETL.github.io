"""TASK 4 - LOAD-READY JSON
Run the full ETL and produce the integrated JSON (saved to output/integrated.json).
"""
import json
from pathlib import Path

from .extract import extract_all
from .transform import transform_all

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def run_pipeline(data_dir=None):
    """Full ETL: extract -> transform. Returns the list of student records."""
    raw = extract_all(data_dir) if data_dir else extract_all()
    return transform_all(raw)


def to_json(records):
    return json.dumps(records, indent=4, ensure_ascii=False)


def save_json(records, path=OUTPUT_DIR / "integrated.json"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_json(records), encoding="utf-8")
    return path


if __name__ == "__main__":
    records = run_pipeline()
    print(to_json(records))
    print(f"\nSaved to {save_json(records)}")
