"""

Name:Declan Murphy
Date:11/24/2024
Assignment:Module 13 Encrypted Message
Due Date:11/24/2024
About this project:Add encrypted message passing to a flask website that displays and updates data from SQLiteDB
Assumptions:Database can contain any data
All work below was performed by Declan Murphy

"""


import socketserver
import sqlite3
from cryptography.fernet import Fernet


# Load the encryption key
def load_key():
    return open("secret.key", "rb").read()


key = load_key()
cipher_suite = Fernet(key)


# Decrypt function
def decrypt_data(data):
    return cipher_suite.decrypt(data).decode()


# Database connection function
def get_db_connection():
    conn = sqlite3.connect('BakingContestDB.db')
    conn.row_factory = sqlite3.Row
    return conn


class VoteHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address[0]} sent message: {self.data}")

        try:
            decrypted_data = decrypt_data(self.data)
            entry_id, excellent_votes, ok_votes, bad_votes = decrypted_data.split('^%$')

            # Validate data
            conn = get_db_connection()
            entry_exists = conn.execute('SELECT 1 FROM BakingContestEntry WHERE EntryId = ?', (entry_id,)).fetchone()

            if not entry_id.isdigit() or int(entry_id) <= 0 or not entry_exists:
                print("Invalid Entry ID")
                return
            if not excellent_votes.isdigit() or int(excellent_votes) < 0:
                print("Invalid number of Excellent Votes")
                return
            if not ok_votes.isdigit() or int(ok_votes) < 0:
                print("Invalid number of OK Votes")
                return
            if not bad_votes.isdigit() or int(bad_votes) < 0:
                print("Invalid number of Bad Votes")
                return

            # Update the database
            conn.execute('''
                UPDATE BakingContestEntry
                SET NumExcellentVotes = NumExcellentVotes + ?,
                    NumOkVotes = NumOkVotes + ?,
                    NumBadVotes = NumBadVotes + ?
                WHERE EntryId = ?
            ''', (excellent_votes, ok_votes, bad_votes, entry_id))
            conn.commit()
            conn.close()

            print(f"entryId: {entry_id}")
            print("Record successfully updated")

        except Exception as e:
            print(f"Error processing vote: {e}")


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socketserver.TCPServer((HOST, PORT), VoteHandler) as server:
        print(f"Server running on {HOST}:{PORT}")
        server.serve_forever()
