import sqlite3

# Connect to your database (change path if needed)
conn = sqlite3.connect("solosafe.db")  # or your DB file name
c = conn.cursor()

# Drop table if it exists (optional, only if you want a fresh start)
c.execute("DROP TABLE IF EXISTS checklist")

# Create checklist table with category and notes
c.execute("""
CREATE TABLE checklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item TEXT,
    status INTEGER,
    category TEXT,
    notes TEXT
)
""")

conn.commit()
conn.close()
print("Checklist table created successfully!")

