from io import BytesIO
import pandas as pd
from attendance import attendance_history
from analytics import student_analytics

def history_csv(student_id=None, class_id=None, start=None, end=None):
    df = pd.DataFrame(attendance_history(student_id, class_id, start, end))
    return df.to_csv(index=False).encode("utf-8")

def summary_csv(student_id=None):
    return student_analytics(student_id).to_csv(index=False).encode("utf-8")

def history_pdf(student_id=None, class_id=None, start=None, end=None):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError as exc:
        raise RuntimeError("Install reportlab to enable PDF export: pip install reportlab") from exc
    df = pd.DataFrame(attendance_history(student_id, class_id, start, end))
    cols = ["attendance_date", "roll_no", "name", "subject_code", "subject_name", "section", "status"]
    if df.empty:
        data = [["No attendance records"]]
    else:
        data = [cols] + df[cols].astype(str).values.tolist()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    story = [Paragraph("Student Attendance Report", styles["Title"]), Spacer(1, 12)]
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#243b53")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
    ]))
    story.append(table); doc.build(story); buf.seek(0)
    return buf.getvalue()
