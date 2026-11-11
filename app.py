import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from database import init_db, query, execute, get_connection
from seed import seed_demo_data
from auth import authenticate, create_user, change_password
from attendance import mark_attendance, attendance_history
from analytics import student_analytics, monthly_analytics, semester_analytics
from calculations import percentage, classes_can_bunk, classes_to_recover, predict
from reports import history_csv, summary_csv, history_pdf

st.set_page_config(page_title="Smart Attendance System", page_icon="🎓", layout="wide")
init_db()
seed_demo_data()
st.title("🎓 Smart Student Attendance Management System")
st.caption("SDG 4 – Quality Education | Attendance, prediction and analytics")

if "user" not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.user = None
    st.rerun()

def login_screen():
    st.subheader("Secure Login")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        user = authenticate(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials or inactive account.")
    with st.expander("Demo login credentials"):
        st.code("Administrator: admin / admin123\nFaculty: faculty1 / faculty123\nStudent: student1 / student123\nStudent: student2 / student123")

def threshold_value():
    row = query("SELECT value FROM settings WHERE key='threshold'")
    return float(row[0]["value"]) if row else 75.0

def current_student():
    rows = query("SELECT * FROM students WHERE user_id=?", (st.session_state.user["id"],))
    return rows[0] if rows else None

def sidebar():
    st.sidebar.write(f"**{st.session_state.user['username']}**")
    st.sidebar.caption(f"Role: {st.session_state.user['role'].title()}")
    if st.sidebar.button("Log out"):
        logout()

def admin_page():
    st.header("Administrator Console")
    tabs = st.tabs(["Overview", "Students", "Faculty", "Subjects & Classes", "Settings", "Reports"])
    with tabs[0]:
        c1,c2,c3,c4 = st.columns(4)
        for col, label, sql in [
            (c1,"Students","SELECT COUNT(*) n FROM students"),
            (c2,"Faculty","SELECT COUNT(*) n FROM faculty"),
            (c3,"Subjects","SELECT COUNT(*) n FROM subjects"),
            (c4,"Attendance entries","SELECT COUNT(*) n FROM attendance")]:
            col.metric(label, query(sql)[0]["n"])
        df = student_analytics()
        if not df.empty:
            st.subheader("Student-subject attendance")
            st.dataframe(df, use_container_width=True)
            low = df[df["percentage"] < threshold_value()]
            if not low.empty:
                st.warning(f"{len(low)} student-subject record(s) are below the attendance threshold.")
                st.dataframe(low[["roll_no", "student_name", "code", "subject_name", "present", "total", "percentage"]], use_container_width=True)
    with tabs[1]:
        st.subheader("Register student")
        with st.form("add_student"):
            username=st.text_input("Login username", key="stu_user")
            password=st.text_input("Temporary password", type="password", key="stu_pass")
            roll=st.text_input("Roll number")
            name=st.text_input("Full name")
            email=st.text_input("Email")
            dept=st.text_input("Department", value="CSE")
            sem=st.text_input("Semester", value="3")
            ok=st.form_submit_button("Create student")
        if ok:
            try:
                uid=create_user(username,password,"student")
                execute("INSERT INTO students(user_id,roll_no,name,email,department,semester) VALUES(?,?,?,?,?,?)",
                        (uid,roll.strip(),name.strip(),email.strip(),dept.strip(),sem.strip()))
                st.success("Student and login created.")
            except Exception as e: st.error(f"Could not create student: {e}")
        students=query("SELECT * FROM students ORDER BY roll_no")
        st.subheader("Student records")
        st.dataframe(pd.DataFrame(students), use_container_width=True)
        if students:
            choice=st.selectbox("Select student to update/delete", students, format_func=lambda x:f"{x['roll_no']} – {x['name']}")
            with st.form("edit_student"):
                newname=st.text_input("Name",choice["name"])
                newemail=st.text_input("Email",choice["email"] or "")
                newdept=st.text_input("Department",choice["department"] or "")
                newsem=st.text_input("Semester",choice["semester"] or "")
                save=st.form_submit_button("Save profile changes")
            if save:
                execute("UPDATE students SET name=?,email=?,department=?,semester=? WHERE id=?",
                        (newname,newemail,newdept,newsem,choice["id"]))
                st.success("Profile updated."); st.rerun()
            if st.button("Delete selected student", type="secondary"):
                execute("DELETE FROM students WHERE id=?",(choice["id"],))
                if choice["user_id"]: execute("DELETE FROM users WHERE id=?",(choice["user_id"],))
                st.success("Student deleted."); st.rerun()
        search=st.text_input("Search by roll number or name")
        if search:
            found=query("SELECT * FROM students WHERE roll_no LIKE ? OR name LIKE ?",
                        (f"%{search}%",f"%{search}%"))
            st.dataframe(pd.DataFrame(found),use_container_width=True)
    with tabs[2]:
        with st.form("add_faculty"):
            u=st.text_input("Faculty username"); p=st.text_input("Temporary password",type="password")
            emp=st.text_input("Employee number"); n=st.text_input("Faculty name")
            em=st.text_input("Faculty email"); d=st.text_input("Department",value="CSE")
            add=st.form_submit_button("Register faculty")
        if add:
            try:
                uid=create_user(u,p,"faculty")
                execute("INSERT INTO faculty(user_id,employee_no,name,email,department) VALUES(?,?,?,?,?)",
                        (uid,emp,n,em,d))
                st.success("Faculty registered.")
            except Exception as e: st.error(f"Could not register faculty: {e}")
        st.dataframe(pd.DataFrame(query("SELECT id,employee_no,name,email,department FROM faculty")),use_container_width=True)
    with tabs[3]:
        st.subheader("Add subject")
        with st.form("subject"):
            code=st.text_input("Subject code"); name=st.text_input("Subject name")
            sem=st.text_input("Semester",value="3"); dept=st.text_input("Department",value="CSE")
            addsub=st.form_submit_button("Add subject")
        if addsub:
            try:
                execute("INSERT INTO subjects(code,name,semester,department) VALUES(?,?,?,?)",(code,name,sem,dept))
                st.success("Subject added.")
            except Exception as e: st.error(f"Could not add subject: {e}")
        st.dataframe(pd.DataFrame(query("SELECT * FROM subjects")),use_container_width=True)
        st.subheader("Create class/section")
        subjects=query("SELECT * FROM subjects"); faculty=query("SELECT * FROM faculty")
        if subjects and faculty:
            with st.form("class"):
                sub=st.selectbox("Subject",subjects,format_func=lambda x:f"{x['code']} – {x['name']}")
                fac=st.selectbox("Faculty",faculty,format_func=lambda x:f"{x['employee_no']} – {x['name']}")
                sec=st.text_input("Section",value="A")
                addcl=st.form_submit_button("Create class")
            if addcl:
                try:
                    execute("INSERT INTO classes(subject_id,faculty_id,section) VALUES(?,?,?)",(sub["id"],fac["id"],sec))
                    st.success("Class created.")
                except Exception as e: st.error(f"Could not create class: {e}")
        st.dataframe(pd.DataFrame(query("""SELECT cl.id,sub.code,sub.name AS subject, f.name AS faculty,cl.section
                                           FROM classes cl JOIN subjects sub ON sub.id=cl.subject_id
                                           JOIN faculty f ON f.id=cl.faculty_id""")),use_container_width=True)
    with tabs[4]:
        threshold=st.number_input("Minimum attendance threshold (%)",min_value=1.0,max_value=99.0,
                                  value=threshold_value(),step=0.5)
        if st.button("Save threshold"):
            execute("UPDATE settings SET value=? WHERE key='threshold'",(str(threshold),))
            st.success("Threshold saved.")
    with tabs[5]:
        start=st.date_input("From date",value=date(date.today().year,1,1))
        end=st.date_input("To date",value=date.today())
        st.download_button("Download attendance CSV",
            history_csv(start=start.isoformat(),end=end.isoformat()),
            file_name="attendance_report.csv",mime="text/csv")
        st.download_button("Download subject summary CSV",summary_csv(),file_name="attendance_summary.csv",mime="text/csv")
        if st.button("Prepare PDF report"):
            try:
                st.download_button("Download PDF",history_pdf(start=start.isoformat(),end=end.isoformat()),
                                   file_name="attendance_report.pdf",mime="application/pdf")
            except Exception as e: st.warning(str(e))
        st.subheader("Monthly attendance report")
        monthly = monthly_analytics(year=start.year)
        if not monthly.empty:
            st.dataframe(monthly, use_container_width=True)
            st.download_button("Download monthly report CSV", monthly.to_csv(index=False).encode("utf-8"),
                               file_name="monthly_attendance_report.csv", mime="text/csv")
        else:
            st.info("No monthly records for the selected start year.")
        st.subheader("Semester-wise attendance report")
        semester = semester_analytics()
        if not semester.empty:
            st.dataframe(semester, use_container_width=True)
            st.download_button("Download semester report CSV", semester.to_csv(index=False).encode("utf-8"),
                               file_name="semester_attendance_report.csv", mime="text/csv")

def faculty_page():
    st.header("Faculty Workspace")
    faculty=query("SELECT * FROM faculty WHERE user_id=?",(st.session_state.user["id"],))
    if not faculty:
        st.error("Faculty profile is not linked to this login. Ask administrator."); return
    classes=query("""SELECT cl.id,cl.section,sub.code,sub.name AS subject
                     FROM classes cl JOIN subjects sub ON sub.id=cl.subject_id
                     WHERE cl.faculty_id=? ORDER BY sub.code""",(faculty[0]["id"],))
    if not classes:
        st.info("No classes assigned yet."); return
    selected=st.selectbox("Choose class",classes,format_func=lambda x:f"{x['code']} – {x['subject']} (Section {x['section']})")
    tab1,tab2=st.tabs(["Mark attendance","History"])
    with tab1:
        students=query("SELECT * FROM students ORDER BY roll_no")
        if students:
            d=st.date_input("Attendance date",value=date.today())
            st.caption("Choose a status for each student. A second submission for the same student/class/date is rejected.")
            choices={}
            for s in students:
                choices[s["id"]]=st.selectbox(f"{s['roll_no']} – {s['name']}",["Present","Absent"],key=f"att_{selected['id']}_{s['id']}_{d}")
            if st.button("Submit attendance"):
                try:
                    saved,skipped=mark_attendance(selected["id"],d.isoformat(),choices.items())
                    st.success(f"Saved {saved} record(s); skipped {skipped} duplicate(s).")
                except Exception as e: st.error(str(e))
    with tab2:
        df=pd.DataFrame(attendance_history(class_id=selected["id"]))
        st.dataframe(df,use_container_width=True)
        if not df.empty:
            st.download_button("Export class history CSV",df.to_csv(index=False).encode(),file_name="class_history.csv")

def student_page():
    st.header("Student Portal")
    student=current_student()
    if not student:
        st.error("Student profile is not linked to this login. Ask administrator."); return
    st.write(f"Welcome, **{student['name']}** · Roll: `{student['roll_no']}` · Semester: {student['semester']}")
    threshold=threshold_value()
    df=student_analytics(student["id"])
    if df.empty:
        st.info("No attendance records available yet.")
    else:
        total=int(df["total"].sum()); present=int(df["present"].sum())
        pct=percentage(present,total)
        c1,c2,c3=st.columns(3)
        c1.metric("Overall attendance",f"{pct:.2f}%")
        c2.metric("Classes attended",f"{present}/{total}")
        c3.metric("Required threshold",f"{threshold:.1f}%")
        if pct < threshold: st.error("⚠️ Attendance shortage: your overall attendance is below the required threshold.")
        else: st.success("Your overall attendance meets the required threshold.")
        st.subheader("Subject-wise attendance")
        st.dataframe(df[["code","subject_name","present","total","percentage"]],use_container_width=True)
        fig,ax=plt.subplots()
        ax.bar(df["code"],df["percentage"])
        ax.axhline(threshold,linestyle="--",label=f"Threshold {threshold:g}%")
        ax.set_ylabel("Attendance (%)"); ax.set_ylim(0,100); ax.legend()
        st.pyplot(fig); plt.close(fig)
        st.subheader("Attendance calculators")
        calc=st.selectbox("Choose calculator",["Bunk calculator","Recovery calculator","Attendance predictor"])
        subject=df.iloc[st.selectbox("Subject row",list(range(len(df))),format_func=lambda i:f"{df.iloc[i]['code']} – {df.iloc[i]['subject_name']}")]
        p=int(subject["present"]); t=int(subject["total"])
        st.caption(f"Selected subject: {subject['code']} · {p}/{t} present ({percentage(p,t):.2f}%)")
        if calc=="Bunk calculator":
            st.metric("Maximum future classes you can miss",classes_can_bunk(p,t,threshold))
        elif calc=="Recovery calculator":
            st.metric("Consecutive classes to attend",classes_to_recover(p,t,threshold))
        else:
            a=st.number_input("Future classes attended",min_value=0,value=5,step=1)
            b=st.number_input("Future classes missed",min_value=0,value=0,step=1)
            result=predict(p,t,int(a),int(b))
            st.metric("Predicted attendance",f"{result['percentage']:.2f}%")
            st.caption(f"Projected total: {result['present']} present out of {result['total']} classes.")
    st.subheader("My attendance history")
    hist=pd.DataFrame(attendance_history(student_id=student["id"]))
    st.dataframe(hist,use_container_width=True)
    st.download_button("Download my attendance CSV",history_csv(student_id=student["id"]),
                       file_name=f"{student['roll_no']}_attendance.csv",mime="text/csv")
    if st.button("Download my PDF report"):
        try:
            st.download_button("Save PDF",history_pdf(student_id=student["id"]),
                               file_name=f"{student['roll_no']}_attendance.pdf",mime="application/pdf")
        except Exception as e: st.warning(str(e))

if st.session_state.user is None:
    login_screen()
else:
    sidebar()
    role=st.session_state.user["role"]
    if role=="admin": admin_page()
    elif role=="faculty": faculty_page()
    elif role=="student": student_page()
