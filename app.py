"""Web application for the CSV ETL exercise (Flask)."""
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from etl.extract import SOURCES
from etl.load import run_pipeline, to_json

# ---- Edit these two lines with your details ----
FULL_NAME = "Full Name Here"
COURSE_SCHEDULE = "IT 3206N [SCHEDULE]"
# ------------------------------------------------

UPLOAD_FIELDS = [
    ("SIS", "Student Information System (SIS)"),
    ("LMS", "Learning Management System (LMS)"),
    ("Accounting", "Accounting System"),
]

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB upload limit
app.json.sort_keys = False  # keep the field order from the data map


def etl_from_upload():
    """Save the 3 uploaded files to a temp folder, run the ETL, then discard them.
    Returns (records, message)."""
    with tempfile.TemporaryDirectory() as tmp:
        for name, label in UPLOAD_FIELDS:
            file = request.files.get(name)
            if not file or not file.filename:
                return None, f"Please upload the {label} CSV file."
            file.save(Path(tmp) / SOURCES[name])
        try:
            return run_pipeline(tmp), "ETL completed successfully."
        except (KeyError, ValueError, UnicodeDecodeError) as exc:
            return None, f"ETL failed: {exc}. Check that each CSV has the expected columns."


def page(**extra):
    return render_template("index.html", full_name=FULL_NAME,
                           schedule=COURSE_SCHEDULE, fields=UPLOAD_FIELDS, **extra)


@app.route("/", methods=["GET", "POST"])
def index():
    """Page. POST is a fallback for browsers with JavaScript disabled."""
    if request.method == "GET":
        return page()
    records, message = etl_from_upload()
    return page(message=message, json_text=to_json(records) if records is not None else None)


@app.route("/etl", methods=["POST"])
def run_etl():
    """Used by the page's JavaScript: returns the ETL result as JSON."""
    records, message = etl_from_upload()
    return jsonify(ok=records is not None, message=message, data=records)


if __name__ == "__main__":
    app.run(debug=True)
