from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

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
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

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
        quantity INTEGER,
        price REAL,
        image TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        quantity INTEGER,
        price REAL,
        image TEXT
    )
    """)

    # default admin
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", ("admin", "1234"))

    # sample products
    cursor.execute("SELECT COUNT(*) FROM Products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO Products (name, description, price, image)
        VALUES (?, ?, ?, ?)
        """, [
            ("Laptop", "Core i5 8GB RAM", 75000,
             "https://tse1.mm.bing.net/th/id/OIP.cmduKem40PZuDvLCz22rqQHaFU?pid=Api&h=220&P=0"),

            ("Mobile", "128GB Storage", 45000,
             "https://tse2.mm.bing.net/th/id/OIP.wk1TPiu8l6DXL27GPTYLdwAAAA?pid=Api&h=220&P=0"),

            ("Headphones", "Wireless", 5000,
             "https://tse3.mm.bing.net/th/id/OIP.pgzU33CxcqL3NvDutVnJTgHaI0?pid=Api&h=220&P=0")
        ])

    conn.commit()
    conn.close()


# ---------------- LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE username=? AND password=?",
                   (data["username"], data["password"]))

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "message": "Login success"})
    return jsonify({"success": False, "message": "Invalid login"})


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
    """, (data["name"], data["description"], data["price"], data["image"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product added"})


# ---------------- DELETE PRODUCT ----------------
@app.route("/api/delete_product/<int:id>", methods=["DELETE"])
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Products WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product deleted"})


# ---------------- CART ----------------
@app.route("/api/cart", methods=["POST"])
def add_cart():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Cart WHERE product_name=?", (data["name"],))
    item = cursor.fetchone()

    if item:
        cursor.execute("UPDATE Cart SET quantity = quantity + 1 WHERE id=?", (item["id"],))
    else:
        cursor.execute("""
        INSERT INTO Cart (product_name, quantity, price, image)
        VALUES (?, ?, ?, ?)
        """, (data["name"], 1, data["price"], data["image"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Added to cart"})


# ---------------- GET CART ----------------
@app.route("/api/cart")
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
        cursor.execute("UPDATE Cart SET quantity=? WHERE id=?",
                       (data["quantity"], data["id"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})


# ---------------- DELETE CART ITEM ----------------
@app.route("/api/cart/<int:id>", methods=["DELETE"])
def delete_cart(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Cart WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted"})


# ---------------- CHECKOUT ----------------
@app.route("/api/checkout", methods=["POST"])
def checkout():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Cart")
    items = cursor.fetchall()

    for i in items:
        cursor.execute("""
        INSERT INTO Orders (product_name, quantity, price, image)
        VALUES (?, ?, ?, ?)
        """, (i["product_name"], i["quantity"], i["price"], i["image"]))

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

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)