import sqlite3

# Path to your SQLite database
db_path = r"C:\Users\arung\OneDrive\Documents\myflask\app.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add the 'country' column if it doesn't exist
try:
    cursor.execute("ALTER TABLE user ADD COLUMN country TEXT;")
    print("Column 'country' added successfully.")
except sqlite3.OperationalError as e:
    print("Could not add column:", e)

conn.commit()
conn.close()
