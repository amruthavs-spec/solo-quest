import sqlite3

DATABASE = "thinkher_travel.db"  # use your actual database name

conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Create budgets table
c.execute("""
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    trip_name TEXT,
    total_budget REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create expenses table
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    trip_name TEXT,
    category TEXT,
    amount REAL,
    date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("Budget tables created!")

