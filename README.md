# Smart Student Attendance Management System

**SDG alignment:** United Nations Sustainable Development Goal 4 – Quality Education.

A modular, database-backed Streamlit application for student, faculty and administrator attendance workflows. It includes attendance entry/history, percentage and shortage checks, bunk/recovery/prediction calculators, analytics, charts and CSV/PDF exports.

## 1. Features

- Three role-based logins: Administrator, Faculty and Student.
- Student and faculty registration/management; student profile update, search and deletion.
- Subject and class/section setup.
- Faculty attendance entry with Present/Absent statuses.
- Duplicate attendance prevention for the same student, class and date (database uniqueness constraint).
- Date-wise, subject-wise and student-wise history.
- Configurable threshold (default 75%); shortage alerts.
- Bunk, recovery and future attendance prediction calculators.
- Student and subject analytics with Matplotlib chart.
- Monthly analytics module and downloadable CSV reports; optional PDF export.
- SQLite persistence and seeded demo data.

## 2. Project structure

```text
smart_attendance_system/
├── app.py              # Streamlit UI and role dashboards
├── config.py           # Paths and defaults
├── database.py         # SQLite schema and database helpers
├── auth.py             # Password hashing and authentication
├── attendance.py       # Attendance entry and history queries
├── calculations.py     # Bunk, recovery and prediction algorithms
├── analytics.py        # Pandas analytics
├── reports.py          # CSV and optional PDF exports
├── seed.py             # Demo accounts and sample attendance
├── requirements.txt
├── README.md
└── data/
    └── attendance.db   # Created automatically on first run
```

## 3. Installation

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The database and demo data are initialized automatically at first launch. The SQLite file is stored in `data/attendance.db`.

### Demo credentials

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Faculty | `faculty1` | `faculty123` |
| Student | `student1` | `student123` |
| Student | `student2` | `student123` |

Change demo passwords before any real deployment. Demo data is seeded only when the `users` table is empty. To reset the demo database, stop the app and delete `data/attendance.db`; it will be recreated on next launch.

## 4. Attendance calculation logic

Let `P` be classes attended, `T` total classes, and `R` the required percentage.

- Percentage: `100 × P / T` (0% when no classes have been recorded).
- Maximum bunkable classes: largest integer `b ≥ 0` satisfying `100P/(T+b) ≥ R`.
- Recovery classes: smallest integer `x ≥ 0` satisfying `100(P+x)/(T+x) ≥ R`.
- Prediction: `100(P+future_present)/(T+future_present+future_absent)`.

Example: 68 attended out of 100, threshold 75%.

`(68 + x) / (100 + x) ≥ 0.75`  
`68 + x ≥ 75 + 0.75x`  
`0.25x ≥ 7`  
`x ≥ 28`

So the student must attend **28 consecutive additional classes** to reach exactly 75%.

## 5. Four-member work distribution

| Member | Suggested ownership | Files / modules |
|---|---|---|
| 1 | Authentication, student/faculty management, database | `auth.py`, `database.py`, admin student/faculty tabs |
| 2 | Subjects/classes, attendance recording and history | `attendance.py`, faculty workspace, subject/class tabs |
| 3 | Calculators and prediction | `calculations.py`, calculator section in student portal |
| 4 | Dashboards, analytics, notifications and exports | `analytics.py`, `reports.py`, chart and reporting sections |

All members integrate against the same SQLite schema. Agree on function signatures and table names before parallel development.

## 6. Testing checklist

1. Login using each demo role and verify the different screens.
2. As admin, add a student, faculty member, subject and class.
3. As faculty, mark attendance for a date.
4. Submit the same class/date again and verify duplicates are skipped.
5. As student, verify only their own summary and history are displayed.
6. Check 68/100 recovery calculation returns 28 at 75%.
7. Try threshold changes (for example 80%) and verify shortage/calculators update.
8. Export CSV; install `reportlab` and test PDF export.
9. Restart Streamlit and confirm records persist in SQLite.

## 7. Notes and limitations

- This is an undergraduate project starter suitable for demonstration and extension, not a hardened production student-information system.
- The sample implementation uses SHA-256 password hashes for simplicity. For production, replace this with a salted password KDF such as Argon2 or bcrypt, add password reset and audit logging, enforce faculty-to-roster assignment, and deploy behind HTTPS.
- Faculty accounts can mark students in the current demo roster. A production build should add explicit class enrolment and restrict faculty to their assigned roster.
- Monthly analytics are provided as a reusable Pandas function; the UI can be extended with month/year filters and semester date boundaries.
- The PDF feature is optional. Install `reportlab` separately if required: `pip install reportlab`.
- Use ISO date format (`YYYY-MM-DD`) for consistent date filtering.
