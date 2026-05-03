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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        quantity INTEGER
    )
    """)

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

# ---------------- LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json

    if data["username"] == "admin" and data["password"] == "1234":
        return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid credentials"})

# ---------------- LOGOUT ----------------
@app.route("/api/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out successfully"})

# ---------------- PRODUCTS ----------------
@app.route("/api/products")
def products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

# ---------------- ADD PRODUCT ----------------
@app.route("/api/add_product", methods=["POST"])
def add_product():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Products (name, description, price)
        VALUES (?, ?, ?)
    """, (data["name"], data["description"], data["price"]))

    conn.commit()
    conn.close()
    return jsonify({"message": "Product added successfully"})

# ---------------- CART ----------------
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

@app.route("/api/cart", methods=["GET"])
def get_cart():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cart")
    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

@app.route("/api/cart/delete", methods=["POST"])
def delete_cart():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Cart WHERE id = ?", (data["id"],))

    conn.commit()
    conn.close()
    return jsonify({"message": "Item removed"})

# ---------------- CHECKOUT ----------------
@app.route("/api/checkout", methods=["POST"])
def checkout():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Cart")
    items = cursor.fetchall()

    for item in items:
        cursor.execute("""
            INSERT INTO Orders (product_name, quantity)
            VALUES (?, ?)
        """, (item["product_name"], item["quantity"]))

    cursor.execute("DELETE FROM Cart")

    conn.commit()
    conn.close()
    return jsonify({"message": "Order placed successfully"})

# ---------------- ORDERS ----------------
@app.route("/api/orders")
def orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders")
    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)