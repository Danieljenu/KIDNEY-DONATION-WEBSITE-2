import sqlite3
import hashlib

DB_NAME = 'donations.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, class_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hashed_pwd = hash_password(password)
    try:
        cursor.execute('INSERT INTO users (username, password, class_name) VALUES (?, ?, ?)',
                       (username, hashed_pwd, class_name))
        conn.commit()
        print(f"User '{username}' for class '{class_name}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists.")
    finally:
        conn.close()

        
if __name__ == '__main__':
    password = "password123"
    for i in range(1, 13):
        class_name = f"{i}A"
        username = f"class{class_name.lower()}"
        add_user(username, password, class_name)
