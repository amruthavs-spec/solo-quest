import sqlite3

DATABASE = "solosafe.db"

conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Create emergency_contacts table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    relationship TEXT,
    phone TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Emergency contacts table ready!")

