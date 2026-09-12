
import PyPDF2
import sqlite3

# Step 1: Connect database (creates file if not exists)
conn = sqlite3.connect("ai_job.db")

# Step 2: Create cursor
c = conn.cursor()

# Step 3: Create USERS table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# Step 4: Create JOBS table
c.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    skills TEXT
)
""")

# Step 5: Save changes
conn.commit()

# Step 6: Close connection
conn.close()

print("✅ Database created successfully with users & jobs table")