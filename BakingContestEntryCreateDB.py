"""

Name: Declan Murphy
Date: 10/27/2024
Assignment: Module 9 SqLite3DB
Due Date: 10/27/20204
About this project: Create DDL and DML scripts in order to form a Python SQLite3DB
Assumptions: Tables can be filled with any data
All work below was performed by Declan Murphy

"""

import sqlite3

# Connect to the SQLite3 database
conn = sqlite3.connect('BakingContestDB.db')
cursor = conn.cursor()

# Drop the BakingContestEntry table if it exists
cursor.execute("DROP TABLE IF EXISTS BakingContestEntry;")

print('BakingContestEntry Table Dropped')

# Create the BakingContestEntry table
cursor.execute('''
CREATE TABLE BakingContestEntry (
    EntryId INTEGER PRIMARY KEY,
    UserId INTEGER,
    NameOfBakingItem TEXT,
    NumExcellentVotes INTEGER,
    NumOkVotes INTEGER,
    NumBadVotes INTEGER,
    FOREIGN KEY (UserId) REFERENCES BakingContestPeople (UserId)
);
''')

# Insert data into the table
entry_data = [
    (1, 1, 'Whoot Whoot Brownies', 1, 2, 4),
    (2, 2, 'Cho Chip Cookies', 4, 1, 2),
    (3, 3, 'Cho Cake', 2, 4, 1),
    (4, 1, 'Sugar Cookies', 2, 2, 1)
]

cursor.executemany('INSERT INTO BakingContestEntry VALUES (?, ?, ?, ?, ?, ?);', entry_data)
conn.commit()

print('BakingContestEntry Table Created')

# Display all rows from the table
cursor.execute('SELECT * FROM BakingContestEntry;')
for entry in cursor.fetchall():
    print(entry)

conn.close()
print('\nConnection Closed')