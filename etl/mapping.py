"""TASK 2 - DATA MAP
Source-to-target mapping used by transform.py.
"""

PROGRAM_MAP = {
    "BSIT": "Bachelor of Science in Information Technology",
    "BSCS": "Bachelor of Science in Computer Science",
    "BSIS": "Bachelor of Science in Information Systems",
}

DATA_MAP = [
    # (source system, source field, target field, target type, rule)
    ("SIS", "student_id", "studentId", "Integer",
     "Convert text to integer; preserve as an identifier (also the join key)."),
    ("SIS", "student_name", "studentName", "String",
     "Trim spaces; normalize to proper case."),
    ("SIS", "program_code", "program", "String",
     "Trim and uppercase code; map to full program name."),
    ("SIS", "email", "emailAddress", "String",
     "Trim spaces; convert to lowercase."),
    ("LMS", "student_id", "(join key)", "Integer",
     "Trim; convert to integer; match the LMS row to the SIS student."),
    ("LMS", "course_code", "lms.courseCode", "String",
     "Trim and uppercase."),
    ("LMS", "final_grade", "lms.finalGrade", "Number or String",
     "Convert numeric grades to number; retain non-numeric values such as INC."),
    ("LMS", "completion_status", "lms.completionStatus", "String",
     "Trim; normalize capitalization consistently."),
    ("Accounting", "student_id", "(join key)", "Integer",
     "Trim; convert to integer; match the Accounting row to the SIS student."),
    ("Accounting", "account_balance", "accounting.outstandingBalance", "Number",
     "Trim and convert to decimal number."),
    ("Accounting", "currency", "accounting.currency", "String",
     "Trim and uppercase."),
]
