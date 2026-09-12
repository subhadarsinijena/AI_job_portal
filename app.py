import streamlit as st
import sqlite3
import PyPDF2
import datetime
import os
import logging


# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI Job Portal", layout="wide")

# ================= CUSTOM CSS =================
st.markdown("""
<style>
[data-testid="metric-container"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

.stButton>button {
    border-radius: 10px;
    height: 45px;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================
conn = sqlite3.connect("ai_job.db", check_same_thread=False)
c = conn.cursor()

# ================= LOGGING SYSTEM =================
LOG_FILE = "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log_event(message):
    logging.info(message)

# ================= TABLES =================
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    skills TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    login_time TEXT,
    logout_time TEXT
)
""")

conn.commit()

# ================= LOCK FILE SYSTEM =================
LOCK_FILE = "app.lock"

def check_system_runtime():

    now = datetime.datetime.now()

    st.sidebar.markdown("## 🔐 System Monitor")

    if not os.path.exists(LOCK_FILE):

        with open(LOCK_FILE, "w") as f:
            f.write(now.isoformat())

        start_time = now

    else:

        with open(LOCK_FILE, "r") as f:
            start_time = datetime.datetime.fromisoformat(f.read())

    diff = now - start_time

    total_seconds = int(diff.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    days = diff.days

    st.sidebar.markdown("### ⏱ Runtime Status")

    col1, col2 = st.sidebar.columns(2)

    col1.metric("📅 Days", days)
    col2.metric("⏰ Hours", hours)

    col3, col4 = st.sidebar.columns(2)

    col3.metric("⏳ Minutes", minutes)
    col4.metric("⌚ Seconds", seconds)

    progress = min(total_seconds / 86400, 1.0)

    st.sidebar.progress(progress)

    if total_seconds < 86400:
        st.sidebar.success("✅ Running Normally")

    elif total_seconds < 172800:
        st.sidebar.warning("⚠️ Running > 24 Hours")

    else:
        st.sidebar.error("🚨 Running > 2 Days")

    st.sidebar.info(
        f"🟢 Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

check_system_runtime()

# ================= SKILL EXTRACTION =================
def extract_skills_from_pdf(file):

    text = ""

    pdf_reader = PyPDF2.PdfReader(file)

    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()

    text = text.lower()

    skills_list = [
        "python",
        "java",
        "c++",
        "html",
        "css",
        "javascript",
        "sql",
        "machine learning",
        "ai",
        "django",
        "flask"
    ]

    return [skill for skill in skills_list if skill in text]

# ================= TITLE =================
st.title("💼 AI Job Portal")

# ================= MENU =================
menu = [
    "Register",
    "Login",
    "Upload Resume",
    "Post Job",
    "Dashboard"
]

choice = st.sidebar.selectbox("Menu", menu)

# ================= REGISTER =================
if choice == "Register":

    st.subheader("📝 Register User")

    name = st.text_input("Name")

    email = st.text_input("Email")

    password = st.text_input("Password", type="password")

    role = st.selectbox(
        "Role",
        ["Candidate", "Recruiter"]
    )

    # REGISTER WITHOUT EMAIL OTP
    if st.button("Register"):

        email_clean = email.strip().lower()

        if not name.strip():
            st.error("Please enter your name")
        elif not email_clean:
            st.error("Please enter your email")
        elif len(password) < 6:
            st.error("Password must be minimum 6 characters")
        else:
            try:
                c.execute(
                    "INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                    (name.strip(), email_clean, password, role)
                )
                conn.commit()

                st.success("Registration Successful ✅")
                log_event(f"REGISTER SUCCESS | {email_clean}")

            except sqlite3.IntegrityError:
                st.error("Email already exists")
            except Exception as e:
                log_event(f"REGISTER ERROR | {email_clean} | {e}")
                st.error("Registration failed. Please try again.")


# ================= LOGIN =================
elif choice == "Login":

    st.subheader("🔑 Login")

    email = st.text_input("Email")

    password = st.text_input("Password", type="password")

    if st.button("Login"):

        c.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = c.fetchone()

        if user:

            st.success(f"Welcome {user[1]} ✅")

            login_time = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            c.execute(
                "INSERT INTO login_logs (username, login_time, logout_time) VALUES (?, ?, '')",
                (user[1], login_time)
            )

            conn.commit()

            st.session_state["user"] = user[1]

            log_event(f"LOGIN SUCCESS | {email}")

        else:

            st.error("Invalid login")

            log_event(f"LOGIN FAILED | {email}")

# ================= LOGOUT =================
if "user" in st.session_state:

    if st.sidebar.button("Logout"):

        logout_time = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        c.execute("""
            UPDATE login_logs
            SET logout_time=?
            WHERE username=? AND logout_time=''
        """, (logout_time, st.session_state["user"]))

        conn.commit()

        log_event(f"LOGOUT | {st.session_state['user']}")

        del st.session_state["user"]

        st.success("Logged out successfully ✅")

# ================= UPLOAD RESUME =================
elif choice == "Upload Resume":

    st.subheader("📄 Upload Resume")

    file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"]
    )

    if file:

        st.success("Resume Uploaded ✅")

        skills = extract_skills_from_pdf(file)

        log_event("RESUME UPLOADED")

        if skills:

            st.subheader("🧠 Extracted Skills")

            st.write(", ".join(skills))

        else:

            st.warning("No skills found")

# ================= POST JOB =================
elif choice == "Post Job":

    st.subheader("💼 Post Job")

    title = st.text_input("Job Title")

    company = st.text_input("Company")

    skills = st.text_input("Skills")

    if st.button("Post Job"):

        if title and company and skills:

            c.execute(
                "INSERT INTO jobs (title,company,skills) VALUES (?,?,?)",
                (title, company, skills)
            )

            conn.commit()

            st.success("Job Added ✅")

            log_event(f"JOB POSTED | {title}")

        else:

            st.warning("Fill all fields")

# ================= DASHBOARD =================
elif choice == "Dashboard":

    st.subheader("📊 Dashboard")

    c.execute("SELECT COUNT(*) FROM users")

    users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM jobs")

    jobs = c.fetchone()[0]

    col1, col2 = st.columns(2)

    col1.metric("👤 Total Users", users)

    col2.metric("💼 Total Jobs", jobs)

    st.markdown("---")

    # USERS
    st.subheader("👤 Users")

    c.execute("SELECT * FROM users")

    st.table(c.fetchall())

    # JOBS
    st.subheader("💼 Jobs")

    c.execute("SELECT * FROM jobs")

    st.table(c.fetchall())

    # LOGIN LOGS
    st.subheader("🕒 Login Logs")

    c.execute("SELECT * FROM login_logs")

    st.table(c.fetchall())

    # SYSTEM LOGS
    st.subheader("🧾 System Logs")

    if os.path.exists(LOG_FILE):

        with open(LOG_FILE, "r") as f:

            logs = f.readlines()

        st.text_area(
            "Application Logs",
            "".join(logs[-50:]),
            height=300
        )

    else:

        st.info("No logs found")