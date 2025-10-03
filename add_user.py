import sqlite3
import hashlib

username = "class10A"
password = "password123"
class_name = "10A"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('donations.db')
cur = conn.cursor()
cur.execute(
    "INSERT INTO users (username, password, class_name) VALUES (?, ?, ?)",
    (username, hash_password(password), class_name)
)
conn.commit()
conn.close()

print("User added!")