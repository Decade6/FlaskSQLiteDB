"""

Name:Declan Murphy
Date:11/17/2024
Assignment:Module 12 Encryption
Due Date:11/17/2024
About this project:Add encryption to a SQLiteDB
Assumptions:Database can contain any data
All work below was performed by Declan Murphy

"""

import sqlite3
from cryptography.fernet import Fernet
import os

# Generate a key and save it
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

# Load the key if it exists, otherwise generate a new one
def load_or_generate_key():
    if os.path.exists("secret.key"):
        return open("secret.key", "rb").read()
    else:
        return generate_key()

# Initialize the Fernet class
key = load_or_generate_key()
cipher_suite = Fernet(key)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('BakingContestDB.db')
    conn.row_factory = sqlite3.Row
    return conn

# Encrypt function
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

# Decrypt function
def decrypt_data(data):
    return cipher_suite.decrypt(data).decode()

# Create and populate the database
conn = get_db_connection()
cursor = conn.cursor()

# Drop existing table
cursor.execute("DROP TABLE IF EXISTS BakingContestPeople;")
print("BakingContestPeople table dropped.")

# Create table
cursor.execute('''
CREATE TABLE BakingContestPeople (
    UserId INTEGER PRIMARY KEY,
    Name BLOB,
    Age INTEGER,
    PhNum BLOB,
    SecurityLevel INTEGER,
    LoginPassword BLOB
);
''')
print("BakingContestPeople Table created.")

# Insert encrypted data
people_data = [
    (1, "PDiana", 34, "123-675-7645", 3, "password1"),
    (2, "TJones", 68, "895-345-6523", 2, "password2"),
    (3, "AMath", 29, "428-197-3967", 3, "password3"),
    (4, "BSmith", 37, "239-567-3498", 1, "password4"),
    (5, "JDoe", 45, "555-123-4567", 2, "password5"),
    (6, "MJohnson", 52, "777-888-9999", 1, "password6")
]

for person in people_data:
    cursor.execute('''
    INSERT INTO BakingContestPeople (UserId, Name, Age, PhNum, SecurityLevel, LoginPassword)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (person[0], encrypt_data(person[1]), person[2], encrypt_data(person[3]), person[4], encrypt_data(person[5])))

conn.commit()

# Display all rows from the table
cursor.execute('SELECT * FROM BakingContestPeople;')
for row in cursor.fetchall():
    print(row['UserId'], row['Name'], row['Age'], row['PhNum'], row['SecurityLevel'], row['LoginPassword'])

conn.close()
print("Connection closed.")

# List of decrypted usernames, passwords, and security levels
print("\nDecrypted User Information:")
for person in people_data:
    print(f"Username: {person[1]}, Password: {person[5]}, Security Level: {person[4]}")

print("\nEncryption key has been generated and saved in 'secret.key'")

# Verify encryption
def verify_encryption():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM BakingContestPeople')
    rows = cursor.fetchall()
    conn.close()

    print("\nVerifying encryption:")
    for row in rows:
        decrypted_name = decrypt_data(row['Name'])
        decrypted_password = decrypt_data(row['LoginPassword'])
        print(f"User: {decrypted_name}, Password: {decrypted_password}")

verify_encryption()

