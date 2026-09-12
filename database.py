import sqlite3

conn = sqlite3.connect("ai_job.db")
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT,
    role TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    skills TEXT
)
''')

conn.commit()
conn.close()