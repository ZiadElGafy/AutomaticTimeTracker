import sqlite3

conn = sqlite3.connect(f'timeTrackingHours.db')
ptr = conn.cursor()
print("Database connection established successfully")

conn.execute('''
             CREATE TABLE hours(
             DATETIME   SMALLDATETIME  NOT NULL,
             CATEGORY   TEXT      NOT NULL,
             ACTIVITY   TEXT      NOT NULL,
             HOURS      INT       NOT NULL
            );
             ''')

print("hours table created successfully")