import sqlite3

DATABASE = "database.db"  # your SQLite DB

conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Create badges table
c.execute("""
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_name TEXT NOT NULL,
    date_earned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("Badges table created/updated successfully!")
