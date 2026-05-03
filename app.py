from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# --------------------------
# DATABASE CONNECTION (SQLite)
# --------------------------
def get_db():
    conn = sqlite3.connect("ecommerce.db")
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------
# HOME ROUTE
# --------------------------
@app.route("/")
def home():
    return "Ecommerce Backend Running Successfully"

# --------------------------
# ADD USER (example)
# --------------------------
@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO Users (name, email, password)
        VALUES (?, ?, ?)
    """, (data["name"], data["email"], data["password"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "User added successfully"})

# --------------------------
# GET USERS
# --------------------------
@app.route("/users")
def get_users():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()

    conn.close()

    return jsonify([dict(u) for u in users])

# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)