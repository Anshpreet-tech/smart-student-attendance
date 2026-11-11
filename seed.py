from database import query, execute
from auth import create_user
from datetime import date, timedelta

def seed_demo_data():
    if query("SELECT id FROM users LIMIT 1"):
        return
    admin_id = create_user("admin", "admin123", "admin")
    fuser = create_user("faculty1", "faculty123", "faculty")
    suser1 = create_user("student1", "student123", "student")
    suser2 = create_user("student2", "student123", "student")
    fid = execute("INSERT INTO faculty(user_id,employee_no,name,email,department) VALUES(?,?,?,?,?)",
                  (fuser, "FAC001", "Dr. Meera Sharma", "meera@example.edu", "CSE"))
    sid1 = execute("INSERT INTO students(user_id,roll_no,name,email,department,semester) VALUES(?,?,?,?,?,?)",
                   (suser1, "CSE23001", "Aarav Singh", "aarav@example.edu", "CSE", "3"))
    sid2 = execute("INSERT INTO students(user_id,roll_no,name,email,department,semester) VALUES(?,?,?,?,?,?)",
                   (suser2, "CSE23002", "Simran Kaur", "simran@example.edu", "CSE", "3"))
    sub1 = execute("INSERT INTO subjects(code,name,semester,department) VALUES(?,?,?,?)",
                   ("CSE301", "Python Programming", "3", "CSE"))
    sub2 = execute("INSERT INTO subjects(code,name,semester,department) VALUES(?,?,?,?)",
                   ("CSE302", "Data Structures", "3", "CSE"))
    cl1 = execute("INSERT INTO classes(subject_id,faculty_id,section) VALUES(?,?,?)", (sub1,fid,"A"))
    cl2 = execute("INSERT INTO classes(subject_id,faculty_id,section) VALUES(?,?,?)", (sub2,fid,"A"))
    today = date.today()
    for i in range(20):
        d = (today - timedelta(days=20-i)).isoformat()
        # 20 Python classes: Aarav 17 present, Simran 14 present
        execute("INSERT INTO attendance(student_id,class_id,attendance_date,status) VALUES(?,?,?,?)",
                (sid1, cl1, d, "Absent" if i in (2, 8, 15) else "Present"))
        execute("INSERT INTO attendance(student_id,class_id,attendance_date,status) VALUES(?,?,?,?)",
                (sid2, cl1, d, "Absent" if i in (1, 3, 5, 7, 9, 11) else "Present"))
        execute("INSERT INTO attendance(student_id,class_id,attendance_date,status) VALUES(?,?,?,?)",
                (sid1, cl2, d, "Absent" if i in (4, 10) else "Present"))
        execute("INSERT INTO attendance(student_id,class_id,attendance_date,status) VALUES(?,?,?,?)",
                (sid2, cl2, d, "Absent" if i in (0, 2, 4, 6, 8, 10, 12, 14) else "Present"))
