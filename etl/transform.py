"""TASK 3 - TRANSFORM
Clean each source row according to the data map, then integrate the 3 sources
using SIS as the master list of students.
"""
from .mapping import PROGRAM_MAP


# ---------- small reusable cleaning helpers ----------

def clean_text(value):
    """Trim leading/trailing spaces and collapse repeated inner spaces. Empty -> None."""
    if value is None:
        return None
    value = " ".join(str(value).split())
    return value or None


def to_proper_case(value):
    """'JUAN dela CRUZ' -> 'Juan Dela Cruz'"""
    value = clean_text(value)
    return value.title() if value else None


def to_upper(value):
    value = clean_text(value)
    return value.upper() if value else None


def to_lower(value):
    value = clean_text(value)
    return value.lower() if value else None


def to_int(value):
    value = clean_text(value)
    return int(value) if value else None


def to_number(value):
    """'5000.00' -> 5000, ' 1500 ' -> 1500, '2500.50' -> 2500.5"""
    value = clean_text(value)
    if value is None:
        return None
    number = float(value.replace(",", ""))
    return int(number) if number.is_integer() else number


def parse_grade(value):
    """Numeric grades -> number ('1.50' -> 1.5).
    Non-numeric values such as INC are kept as uppercase text, NOT forced into a number:
    INC is a status (Incomplete), not a score. Converting it to 0 or 5.0 would invent
    a grade the student never received and distort averages.
    """
    try:
        return to_number(value)
    except ValueError:
        return to_upper(value)


# ---------- transform each source ----------

def transform_sis(row):
    code = to_upper(row.get("program_code"))
    return {
        "studentId": to_int(row.get("student_id")),
        "studentName": to_proper_case(row.get("student_name")),
        "program": PROGRAM_MAP.get(code, code),
        "emailAddress": to_lower(row.get("email")),
    }


def transform_lms(row):
    return {
        "courseCode": to_upper(row.get("course_code")),
        "finalGrade": parse_grade(row.get("final_grade")),
        "completionStatus": to_proper_case(row.get("completion_status")),
    }


def transform_accounting(row):
    return {
        "outstandingBalance": to_number(row.get("account_balance")),
        "currency": to_upper(row.get("currency")),
    }


# ---------- integrate ----------

def transform_all(raw):
    """raw = output of extract_all(). Returns the list of integrated student records.

    SIS is the master source (LEFT JOIN on studentId):
    - every SIS student is kept, even with no LMS / Accounting data (-> null);
    - LMS / Accounting rows whose ID is not in SIS (e.g. 1005) are not loaded,
      because the student cannot be confirmed without an SIS record.
    """
    lms_by_id = {}
    for row in raw["LMS"]:
        lms_by_id.setdefault(to_int(row["student_id"]), transform_lms(row))

    acct_by_id = {}
    for row in raw["Accounting"]:
        acct_by_id.setdefault(to_int(row["student_id"]), transform_accounting(row))

    students = []
    for row in raw["SIS"]:
        student = transform_sis(row)
        student["lms"] = lms_by_id.get(student["studentId"])
        student["accounting"] = acct_by_id.get(student["studentId"])
        students.append(student)
    return students


if __name__ == "__main__":
    import json
    from .extract import extract_all
    print(json.dumps(transform_all(extract_all()), indent=4))
