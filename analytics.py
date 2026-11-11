import pandas as pd
from attendance import subject_summary, attendance_history
from calculations import percentage

def student_analytics(student_id=None):
    rows = subject_summary(student_id)
    for r in rows:
        r["percentage"] = percentage(r["present"] or 0, r["total"] or 0)
    return pd.DataFrame(rows)

def monthly_analytics(student_id=None, year=None):
    rows = attendance_history(student_id=student_id)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["attendance_date"] = pd.to_datetime(df["attendance_date"])
    if year:
        df = df[df["attendance_date"].dt.year == int(year)]
    df["month"] = df["attendance_date"].dt.strftime("%Y-%m")
    result = (df.assign(is_present=df["status"].eq("Present"))
                .groupby(["month", "subject_code", "subject_name"], as_index=False)
                .agg(total=("status", "size"), present=("is_present", "sum")))
    result["percentage"] = result["present"] / result["total"] * 100
    return result


def semester_analytics():
    """Aggregate attendance by student and subject semester."""
    from database import query
    rows = query("""SELECT st.roll_no, st.name AS student_name, st.semester AS student_semester,
                         sub.semester AS subject_semester, sub.code, sub.name AS subject_name,
                         COUNT(a.id) AS total,
                         SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present
                  FROM attendance a
                  JOIN students st ON st.id=a.student_id
                  JOIN classes cl ON cl.id=a.class_id
                  JOIN subjects sub ON sub.id=cl.subject_id
                  GROUP BY st.id, sub.id ORDER BY sub.semester, st.roll_no, sub.code""")
    df = pd.DataFrame(rows)
    if not df.empty:
        df["percentage"] = df["present"] / df["total"] * 100
    return df
