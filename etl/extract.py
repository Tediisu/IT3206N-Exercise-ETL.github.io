"""TASK 1 - EXTRACT
Read each source CSV into a list of dictionaries (one dict per row).
Values are kept exactly as they appear in the file (raw text) -
cleaning happens later in the TRANSFORM step.
"""
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SOURCES = {
    "SIS": "source_A_SIS.csv",
    "LMS": "source_B_LMS.csv",
    "Accounting": "source_C_Accounting.csv",
}

# Columns each source file must contain (used to reject the wrong file).
REQUIRED_COLUMNS = {
    "SIS": {"student_id", "student_name", "program_code", "email"},
    "LMS": {"student_id", "course_code", "final_grade", "completion_status"},
    "Accounting": {"student_id", "account_balance", "currency"},
}


def read_csv(path):
    """Return the rows of a CSV file as a list of dicts."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def extract_all(data_dir=DATA_DIR):
    """Extract all 3 sources. Returns {"SIS": [...], "LMS": [...], "Accounting": [...]}."""
    data = {}
    for name, filename in SOURCES.items():
        rows = read_csv(Path(data_dir) / filename)
        columns = {c.strip() for c in rows[0].keys()} if rows else set()
        missing = REQUIRED_COLUMNS[name] - columns
        if missing:
            raise ValueError(f"{name} file is missing column(s): {', '.join(sorted(missing))}")
        data[name] = rows
    return data


if __name__ == "__main__":
    import json
    print(json.dumps(extract_all(), indent=2))
