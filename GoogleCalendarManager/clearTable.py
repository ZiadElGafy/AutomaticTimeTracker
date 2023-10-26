import sqlite3

conn = sqlite3.connect(f'timeTrackingHours.db')
ptr = conn.cursor()
print("Database connection established successfully")

conn.execute('DELETE FROM HOURS;')
conn.commit()

print("hours table cleared successfully")