import sqlite3

# Use the same database file your app uses
DATABASE = "solosafe.db"  # Replace with your actual database name if different

conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Create the emergency_contacts table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS emergency_contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    relationship TEXT,
    phone TEXT
)
''')

conn.commit()
conn.close()
print("✅ emergency_contacts table created successfully!")

