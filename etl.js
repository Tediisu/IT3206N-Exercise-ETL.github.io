const PROGRAM_MAP = {
  BSIT: "Bachelor of Science in Information Technology",
  BSCS: "Bachelor of Science in Computer Science",
  BSIS: "Bachelor of Science in Information Systems",
};

const DATA_MAP = [
  ["SIS", "student_id", "studentId", "Integer", "Convert text to integer; preserve as an identifier (also the join key)."],
  ["SIS", "student_name", "studentName", "String", "Trim spaces; normalize to proper case."],
  ["SIS", "program_code", "program", "String", "Trim and uppercase code; map to full program name."],
  ["SIS", "email", "emailAddress", "String", "Trim spaces; convert to lowercase."],
  ["LMS", "student_id", "(join key)", "Integer", "Trim; convert to integer; match the LMS row to the SIS student."],
  ["LMS", "course_code", "lms.courseCode", "String", "Trim and uppercase."],
  ["LMS", "final_grade", "lms.finalGrade", "Number or String", "Convert numeric grades to number; retain non-numeric values such as INC."],
  ["LMS", "completion_status", "lms.completionStatus", "String", "Trim; normalize capitalization consistently."],
  ["Accounting", "student_id", "(join key)", "Integer", "Trim; convert to integer; match the Accounting row to the SIS student."],
  ["Accounting", "account_balance", "accounting.outstandingBalance", "Number", "Trim and convert to decimal number."],
  ["Accounting", "currency", "accounting.currency", "String", "Trim and uppercase."],
];

const REQUIRED_COLUMNS = {
  SIS: ["student_id", "student_name", "program_code", "email"],
  LMS: ["student_id", "course_code", "final_grade", "completion_status"],
  Accounting: ["student_id", "account_balance", "currency"],
};

function parseCsv(text) {
  text = text.replace(/^﻿/, ""); 
  const rows = [];
  let row = [], value = "", inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"' && text[i + 1] === '"') { value += '"'; i++; }
      else if (ch === '"') inQuotes = false;
      else value += ch;
    } else if (ch === '"') inQuotes = true;
    else if (ch === ",") { row.push(value); value = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(value); rows.push(row); row = []; value = "";
    } else value += ch;
  }
  if (value !== "" || row.length) { row.push(value); rows.push(row); }

  const nonEmpty = rows.filter(r => r.some(v => v.trim() !== ""));
  if (!nonEmpty.length) return [];
  const header = nonEmpty[0].map(h => h.trim());
  return nonEmpty.slice(1).map(r => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ""])));
}

function extract(name, text) {
  const rows = parseCsv(text);
  const columns = rows.length ? Object.keys(rows[0]) : [];
  const missing = REQUIRED_COLUMNS[name].filter(c => !columns.includes(c));
  if (missing.length) throw new Error(`${name} file is missing column(s): ${missing.join(", ")}`);
  return rows;
}

function cleanText(value) {
  if (value === null || value === undefined) return null;
  const v = String(value).trim().replace(/\s+/g, " ");
  return v === "" ? null : v;
}

function toProperCase(value) {
  const v = cleanText(value);
  return v === null ? null
    : v.toLowerCase().replace(/(^|[^a-z])([a-z])/g, (m, before, letter) => before + letter.toUpperCase());
}

function toUpper(value) { const v = cleanText(value); return v === null ? null : v.toUpperCase(); }
function toLower(value) { const v = cleanText(value); return v === null ? null : v.toLowerCase(); }

function toInt(value) {
  const v = cleanText(value);
  if (v === null) return null;
  if (!/^[+-]?\d+$/.test(v)) throw new Error(`Invalid student ID: "${v}"`);
  return parseInt(v, 10);
}

function toNumber(value) {
  const v = cleanText(value);
  if (v === null) return null;
  const s = v.replace(/,/g, "");
  return /^[+-]?(\d+\.?\d*|\.\d+)$/.test(s) ? Number(s) : NaN;
}

function parseGrade(value) {
  const n = toNumber(value);
  return Number.isNaN(n) ? toUpper(value) : n;
}

function transformSis(row) {
  const code = toUpper(row.program_code);
  return {
    studentId: toInt(row.student_id),
    studentName: toProperCase(row.student_name),
    program: PROGRAM_MAP[code] ?? code,
    emailAddress: toLower(row.email),
  };
}

function transformLms(row) {
  return {
    courseCode: toUpper(row.course_code),
    finalGrade: parseGrade(row.final_grade),
    completionStatus: toProperCase(row.completion_status),
  };
}

function transformAccounting(row) {
  const balance = toNumber(row.account_balance);
  if (Number.isNaN(balance)) throw new Error(`Invalid account balance: "${cleanText(row.account_balance)}"`);
  return { outstandingBalance: balance, currency: toUpper(row.currency) };
}

function runEtl(files) {
  const sis = extract("SIS", files.SIS);
  const lms = extract("LMS", files.LMS);
  const accounting = extract("Accounting", files.Accounting);

  const lmsById = new Map();
  for (const row of lms) {
    const id = toInt(row.student_id);
    if (!lmsById.has(id)) lmsById.set(id, transformLms(row));
  }
  const acctById = new Map();
  for (const row of accounting) {
    const id = toInt(row.student_id);
    if (!acctById.has(id)) acctById.set(id, transformAccounting(row));
  }

  return sis.map(row => {
    const student = transformSis(row);
    student.lms = lmsById.get(student.studentId) ?? null;
    student.accounting = acctById.get(student.studentId) ?? null;
    return student;
  });
}

if (typeof module !== "undefined") module.exports = { runEtl, parseCsv, DATA_MAP, PROGRAM_MAP };
