from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE ----------------
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
        price REAL,
        image TEXT
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

    # sample data
    cursor.execute("SELECT COUNT(*) FROM Products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO Products (name, description, price, image)
        VALUES (?, ?, ?, ?)
        """, [
            ("Laptop", "Core i5 8GB RAM", 75000, "https://via.placeholder.com/200"),
            ("Mobile", "128GB Storage", 45000, "https://via.placeholder.com/200"),
            ("Headphones", "Wireless", 5000, "https://via.placeholder.com/200")
        ])

    conn.commit()
    conn.close()

# ---------------- LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data"})

    if data.get("username") == "admin" and data.get("password") == "1234":
        return jsonify({"success": True, "message": "Login successful"})

    return jsonify({"success": False, "message": "Invalid credentials"})


# ---------------- LOGOUT ----------------
@app.route("/api/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out"})


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
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Products (name, description, price, image)
    VALUES (?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("description"),
        data.get("price"),
        data.get("image")
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product added"})


# ---------------- ADD TO CART ----------------
@app.route("/api/cart", methods=["POST"])
def add_cart():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Cart WHERE product_name=?", (data["name"],))
    item = cursor.fetchone()

    if item:
        cursor.execute("""
        UPDATE Cart SET quantity = quantity + 1
        WHERE id = ?
        """, (item["id"],))
    else:
        cursor.execute("""
        INSERT INTO Cart (product_name, quantity)
        VALUES (?, ?)
        """, (data["name"], 1))

    conn.commit()
    conn.close()

    return jsonify({"message": "Added to cart"})


# ---------------- GET CART ----------------
@app.route("/api/cart", methods=["GET"])
def get_cart():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cart")
    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])


# ---------------- UPDATE CART ----------------
@app.route("/api/cart/update", methods=["POST"])
def update_cart():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    if data["quantity"] <= 0:
        cursor.execute("DELETE FROM Cart WHERE id=?", (data["id"],))
    else:
        cursor.execute("""
        UPDATE Cart SET quantity=?
        WHERE id=?
        """, (data["quantity"], data["id"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Cart updated"})


# ---------------- DELETE ITEM ----------------
@app.route("/api/cart/<int:id>", methods=["DELETE"])
def delete_item(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cart WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item deleted"})


# ---------------- CHECKOUT ----------------
@app.route("/api/checkout", methods=["POST"])
def checkout():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Cart")
    items = cursor.fetchall()

    for i in items:
        cursor.execute("""
        INSERT INTO Orders (product_name, quantity)
        VALUES (?, ?)
        """, (i["product_name"], i["quantity"]))

    cursor.execute("DELETE FROM Cart")

    conn.commit()
    conn.close()

    return jsonify({"message": "Order placed"})


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
    app.run(host="0.0.0.0", port=10000, debug=True)