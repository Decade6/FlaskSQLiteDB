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

# Delete a specific row
cursor.execute("DELETE FROM BakingContestPeople WHERE Name = 'BSmith';")
conn.commit()

print("Delete BSmith")
cursor.execute('SELECT * FROM BakingContestPeople;')
for person in cursor.fetchall():
    print(person)

# Update a specific row
cursor.execute("UPDATE BakingContestPeople SET Age = 33 WHERE Name = 'AMath';")
conn.commit()

print("\nUpdate Age = 33 for AMath")
cursor.execute('SELECT * FROM BakingContestPeople;')
for person in cursor.fetchall():
    print(person)

# Select all data from the table
print("\nA select statement that selects data from a single table")
cursor.execute('SELECT * FROM BakingContestPeople;')
for person in cursor.fetchall():
    print(person)

# Select specific columns
print("\nA select statement that selects data from a single table that limits the columns returned;")
cursor.execute('SELECT Name, Age FROM BakingContestPeople;')
for person in cursor.fetchall():
    print(person)

# Select with a limit
print("\nA select statement that selects data from a single table that limits the rows returned;")
cursor.execute('SELECT * FROM BakingContestPeople LIMIT 2;')
for person in cursor.fetchall():
    print(person)

# Select specific columns with a limit
print("\nA select statement that selects data from a single table that limits the columns and rows returned;")
cursor.execute('SELECT Name, Age FROM BakingContestPeople LIMIT 2;')
for person in cursor.fetchall():
    print(person)

conn.close()
print('\nConnection Closed')