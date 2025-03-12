"""

Name:Declan Murphy
Date:11/24/2024
Assignment:Module 13 Encrypted Message
Due Date:11/24/2024
About this project:Add encrypted message passing to a flask website that displays and updates data from SQLiteDB
Assumptions:Database can contain any data
All work below was performed by Declan Murphy

"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.urandom(24)


# Load the key
def load_key():
    return open("secret.key", "rb").read()


# Initialize the Fernet class
key = load_key()
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


@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Attempting login with username: {username}")  # Debug print

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM BakingContestPeople')
        users = cursor.fetchall()
        conn.close()

        for user in users:
            decrypted_username = decrypt_data(user['Name'])
            if decrypted_username == username:
                print(f"User found: {decrypted_username}")  # Debug print
                decrypted_password = decrypt_data(user['LoginPassword'])
                if password == decrypted_password:
                    session['user_id'] = user['UserId']
                    session['username'] = decrypted_username
                    session['security_level'] = user['SecurityLevel']
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('home'))
                else:
                    print("Password mismatch")  # Debug print
                    break

        flash('Invalid username and/or password!', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session or session['security_level'] != 3:
        flash('Access denied!', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']
        security_level = request.form['security_level']
        password = request.form['password']

        # Input validation
        errors = []
        if not name.strip():
            errors.append("Name cannot be empty")
        if not age.isdigit() or int(age) <= 0 or int(age) >= 121:
            errors.append("Age must be a whole number between 1 and 120")
        if not phone.strip():
            errors.append("Phone number cannot be empty")
        if not security_level.isdigit() or int(security_level) < 1 or int(security_level) > 3:
            errors.append("Security level must be 1, 2, or 3")
        if not password.strip():
            errors.append("Password cannot be empty")

        if errors:
            return redirect(url_for('results', msg=", ".join(errors)))
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO BakingContestPeople (Name, Age, PhNum, SecurityLevel, LoginPassword) VALUES (?, ?, ?, ?, ?)',
                (encrypt_data(name), age, encrypt_data(phone), security_level, encrypt_data(password)))
            conn.commit()
            conn.close()
            return redirect(url_for('results', msg="User added successfully"))

    return render_template('add_user.html')


@app.route('/list_users')
def list_users():
    if 'user_id' not in session or session['security_level'] < 2:
        flash('Access denied!', 'error')
        return redirect(url_for('home'))

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM BakingContestPeople').fetchall()
    conn.close()

    decrypted_users = []
    for user in users:
        decrypted_users.append({
            'Name': decrypt_data(user['Name']),
            'Age': user['Age'],
            'PhNum': decrypt_data(user['PhNum']),
            'SecurityLevel': user['SecurityLevel'],
            'LoginPassword': decrypt_data(user['LoginPassword'])
        })

    return render_template('list_users.html', users=decrypted_users)


@app.route('/contest_results')
def contest_results():
    if 'user_id' not in session or session['security_level'] != 3:
        flash('Access denied!', 'error')
        return redirect(url_for('home'))

    conn = get_db_connection()
    results = conn.execute('SELECT * FROM BakingContestEntry').fetchall()
    conn.close()
    return render_template('contest_results.html', results=results)


@app.route('/my_results')
def my_results():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    results = conn.execute(
        'SELECT NameOfBakingItem, NumExcellentVotes, NumOkVotes, NumBadVotes FROM BakingContestEntry WHERE UserId = ?',
        (session['user_id'],)).fetchall()
    conn.close()
    return render_template('my_results.html', results=results)


@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        excellent_votes = request.form['excellent_votes']
        ok_votes = request.form['ok_votes']
        bad_votes = request.form['bad_votes']

        # Input validation
        errors = []
        if not name.strip():
            errors.append("Name of baking item cannot be empty")
        if not excellent_votes.isdigit() or int(excellent_votes) < 0:
            errors.append("Number of excellent votes must be a whole number greater than or equal to 0")
        if not ok_votes.isdigit() or int(ok_votes) < 0:
            errors.append("Number of OK votes must be a whole number greater than or equal to 0")
        if not bad_votes.isdigit() or int(bad_votes) < 0:
            errors.append("Number of bad votes must be a whole number greater than or equal to 0")

        if errors:
            return redirect(url_for('results', msg=", ".join(errors)))
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO BakingContestEntry (UserId, NameOfBakingItem, NumExcellentVotes, NumOkVotes, NumBadVotes) VALUES (?, ?, ?, ?, ?)',
                (session['user_id'], name, excellent_votes, ok_votes, bad_votes))
            conn.commit()
            conn.close()
            return redirect(url_for('results', msg="Contest entry added successfully"))

    return render_template('add_entry.html')


@app.route('/results')
def results():
    msg = request.args.get('msg', '')
    return render_template('results.html', msg=msg)


@app.route('/submit_vote', methods=['GET', 'POST'])
def submit_vote():
    if 'user_id' not in session or session['security_level'] < 2:
        flash('Access denied!', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        entry_id = request.form['entry_id']
        excellent_votes = request.form['excellent_votes']
        ok_votes = request.form['ok_votes']
        bad_votes = request.form['bad_votes']

        # Input validation
        errors = []
        conn = get_db_connection()
        entry_exists = conn.execute('SELECT 1 FROM BakingContestEntry WHERE EntryId = ?', (entry_id,)).fetchone()
        conn.close()

        if not entry_id.isdigit() or int(entry_id) <= 0 or not entry_exists:
            errors.append("Invalid Entry ID")
        if not excellent_votes.isdigit() or int(excellent_votes) < 0:
            errors.append("Number of Excellent Votes must be a non-negative integer")
        if not ok_votes.isdigit() or int(ok_votes) < 0:
            errors.append("Number of OK Votes must be a non-negative integer")
        if not bad_votes.isdigit() or int(bad_votes) < 0:
            errors.append("Number of Bad Votes must be a non-negative integer")

        if errors:
            return redirect(url_for('results', msg=", ".join(errors)))
        else:
            # Prepare the message
            message = f"{entry_id}^%${excellent_votes}^%${ok_votes}^%${bad_votes}"
            encrypted_message = encrypt_data(message)

            # Send the message to the server
            import socket
            HOST, PORT = "localhost", 9999
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((HOST, PORT))
                    sock.sendall(encrypted_message)
                return redirect(url_for('results', msg="Vote successfully sent"))
            except Exception as e:
                print(f"Error sending vote: {e}")
                return redirect(url_for('results', msg="Error - Vote NOT sent"))

    return render_template('submit_vote.html')


if __name__ == '__main__':
    app.run(debug=True)
