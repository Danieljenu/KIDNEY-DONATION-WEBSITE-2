from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib


app = Flask(__name__)
CORS(app)


DB_NAME = 'donations.db'


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            class_name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_no TEXT NOT NULL,
            amount INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and user['password'] == hash_password(password):
        return jsonify({"success": True, "class_name": user['class_name'], "user_id": user["id"]})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


@app.route('/api/add_donation', methods=['POST'])
def add_donation():
    data = request.json
    admission_no = data.get('admissionNo')
    amount = data.get('amount')
    user_id = data.get('userId')

    if not admission_no or not amount or not user_id:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    try:
        amount = int(amount)
        if amount <= 0:
            raise ValueError
    except:
        return jsonify({"success": False, "message": "Invalid amount"}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO donations (admission_no, amount, user_id) VALUES (?, ?, ?)',
                 (admission_no, amount, user_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route('/api/delete_donation', methods=['POST'])
def delete_donation():
    data = request.json
    admission_no = data.get('admissionNo')
    user_id = data.get('userId')

    if not admission_no or not user_id:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM donations WHERE admission_no = ? AND user_id = ?', (admission_no, user_id))
    changes = cursor.rowcount
    conn.commit()
    conn.close()

    if changes > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Donation not found"}), 404


@app.route('/api/search', methods=['GET'])
def search():
    admission_no = request.args.get('admission')
    if not admission_no:
        return jsonify({"total": 0})

    conn = get_db_connection()
    row = conn.execute('SELECT SUM(amount) as total FROM donations WHERE admission_no = ?', (admission_no,)).fetchone()
    conn.close()

    total = row['total'] if row['total'] else 0
    # returning numeric total only for clarity and consistency
    return jsonify({"total": total})


@app.route('/api/total-donations')
def total_donations():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT SUM(amount) as total FROM donations')
    total = cur.fetchone()['total'] or 0
    conn.close()
    return jsonify({'total': total})


@app.route('/api/progress', methods=['GET'])
def progress():
    goal = 750000
    conn = get_db_connection()
    row = conn.execute('SELECT SUM(amount) as total FROM donations').fetchone()
    conn.close()
    total = row['total'] if row['total'] else 0
    percent = round((total / goal) * 100) if goal else 0
    return jsonify({"raised": total, "goal": goal, "percent": percent})


@app.route('/api/class_leaderboard', methods=['GET'])
def leaderboard():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT u.class_name as class, SUM(d.amount) as total 
        FROM donations d INNER JOIN users u ON d.user_id = u.id
        GROUP BY u.class_name ORDER BY total DESC
    ''').fetchall()
    conn.close()
    classes = [{"class": r["class"], "total": r["total"]} for r in rows]
    return jsonify({"classes": classes})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
