import sqlite3

# Step 1: Connect/Create database file
conn = sqlite3.connect("job_portal.db")

# Step 2: Create cursor (used to run SQL commands)
c = conn.cursor()

# Step 3: Create users table (IMPORTANT FIX)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT,
    role TEXT
)
""")

# Step 4: Save changes
conn.commit()

# Step 5: Close connection
conn.close()

print("✅ Database and users table created successfully")