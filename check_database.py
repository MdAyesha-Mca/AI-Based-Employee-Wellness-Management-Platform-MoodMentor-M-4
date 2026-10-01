import sqlite3

db_path = "../milestone3/moodmentor.db"

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)

tables = cursor.fetchall()

print("Tables in MoodMentor database:")
print(tables)

conn.close()     