from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect("ecommerce.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- INIT DB ----------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        quantity INTEGER
    )
    """)

    # sample data (only first time)
    cursor.execute("SELECT COUNT(*) FROM Products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO Products (name, description, price)
        VALUES (?, ?, ?)
        """, [
            ("Laptop", "Core i5 8GB RAM", 75000),
            ("Mobile", "128GB Storage", 45000),
            ("Headphones", "Wireless", 5000)
        ])

    conn.commit()
    conn.close()

# ---------------- API: PRODUCTS ----------------
@app.route("/api/products")
def products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

# ---------------- API: ADD TO CART ----------------
@app.route("/api/cart", methods=["POST"])
def add_cart():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Cart (product_name, quantity)
        VALUES (?, ?)
    """, (data["name"], 1))

    conn.commit()
    conn.close()

    return jsonify({"message": "Added to cart"})

# ---------------- INIT + RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)