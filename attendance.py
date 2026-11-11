from database import query, execute

def mark_attendance(class_id, attendance_date, records):
    """records is iterable of (student_id, 'Present'|'Absent'); atomic per record."""
    saved, skipped = 0, 0
    for student_id, status in records:
        if status not in ("Present", "Absent"):
            raise ValueError("Status must be Present or Absent.")
        try:
            execute("""INSERT INTO attendance(student_id,class_id,attendance_date,status)
                        VALUES(?,?,?,?)""", (student_id, class_id, attendance_date, status))
            saved += 1
        except Exception as exc:
            if "UNIQUE constraint failed" in str(exc):
                skipped += 1
            else:
                raise
    return saved, skipped

def attendance_history(student_id=None, class_id=None, start=None, end=None):
    sql = """SELECT a.id, a.attendance_date, a.status, s.roll_no, s.name,
                    sub.code AS subject_code, sub.name AS subject_name,
                    cl.section, f.name AS faculty_name
             FROM attendance a
             JOIN students s ON s.id=a.student_id
             JOIN classes cl ON cl.id=a.class_id
             JOIN subjects sub ON sub.id=cl.subject_id
             JOIN faculty f ON f.id=cl.faculty_id WHERE 1=1"""
    params = []
    if student_id is not None:
        sql += " AND a.student_id=?"; params.append(student_id)
    if class_id is not None:
        sql += " AND a.class_id=?"; params.append(class_id)
    if start:
        sql += " AND a.attendance_date>=?"; params.append(start)
    if end:
        sql += " AND a.attendance_date<=?"; params.append(end)
    sql += " ORDER BY a.attendance_date DESC, sub.code"
    return query(sql, params)

def subject_summary(student_id=None):
    sql = """SELECT s.id AS student_id, s.roll_no, s.name AS student_name,
                    sub.id AS subject_id, sub.code, sub.name AS subject_name,
                    COUNT(a.id) AS total,
                    SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present
             FROM attendance a JOIN students s ON s.id=a.student_id
             JOIN classes cl ON cl.id=a.class_id
             JOIN subjects sub ON sub.id=cl.subject_id"""
    params = []
    if student_id is not None:
        sql += " WHERE s.id=?"; params.append(student_id)
    sql += " GROUP BY s.id, sub.id ORDER BY s.name, sub.code"
    return query(sql, params)
