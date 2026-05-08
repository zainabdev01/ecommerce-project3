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


# ---------------- INIT DATABASE ----------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # PRODUCTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL,
        image TEXT
    )
    """)

    # CART TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        quantity INTEGER
    )
    """)

    # ORDERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        quantity INTEGER
    )
    """)

    # INSERT SAMPLE PRODUCTS ONLY FIRST TIME
    cursor.execute("SELECT COUNT(*) FROM Products")

    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO Products (name, description, price, image)
        VALUES (?, ?, ?, ?)
        """, [
            (
                "Laptop",
                "Core i5 8GB RAM",
                75000,
                "https://via.placeholder.com/200"
            ),
            (
                "Mobile",
                "128GB Storage",
                45000,
                "https://via.placeholder.com/200"
            ),
            (
                "Headphones",
                "Wireless Headphones",
                5000,
                "https://via.placeholder.com/200"
            )
        ])

    conn.commit()
    conn.close()


# ---------------- LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        })

    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "1234":
        return jsonify({
            "success": True,
            "message": "Login successful"
        })

    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    })


# ---------------- LOGOUT ----------------
@app.route("/api/logout", methods=["POST"])
def logout():
    return jsonify({
        "message": "Logged out successfully"
    })


# ---------------- GET PRODUCTS ----------------
@app.route("/api/products", methods=["GET"])
def get_products():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in products])


# ---------------- ADD PRODUCT ----------------
@app.route("/api/add_product", methods=["POST"])
def add_product():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No data received"
        }), 400

    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    image = data.get("image")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Products (name, description, price, image)
    VALUES (?, ?, ?, ?)
    """, (name, description, price, image))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Product added successfully"
    })


# ---------------- ADD TO CART ----------------
@app.route("/api/cart", methods=["POST"])
def add_to_cart():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No data received"
        }), 400

    product_name = data.get("name")

    conn = get_db()
    cursor = conn.cursor()

    # CHECK IF PRODUCT ALREADY EXISTS
    cursor.execute("""
    SELECT * FROM Cart
    WHERE product_name = ?
    """, (product_name,))

    item = cursor.fetchone()

    if item:
        # INCREASE QUANTITY
        cursor.execute("""
        UPDATE Cart
        SET quantity = quantity + 1
        WHERE id = ?
        """, (item["id"],))

    else:
        # INSERT NEW ITEM
        cursor.execute("""
        INSERT INTO Cart (product_name, quantity)
        VALUES (?, ?)
        """, (product_name, 1))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Added to cart"
    })


# ---------------- GET CART ITEMS ----------------
@app.route("/api/cart", methods=["GET"])
def get_cart():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Cart")
    items = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in items])


# ---------------- UPDATE CART QUANTITY ----------------
@app.route("/api/cart/update", methods=["POST"])
def update_cart():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No data received"
        }), 400

    item_id = data.get("id")
    quantity = data.get("quantity")

    conn = get_db()
    cursor = conn.cursor()

    # REMOVE ITEM IF QUANTITY <= 0
    if quantity <= 0:

        cursor.execute("""
        DELETE FROM Cart
        WHERE id = ?
        """, (item_id,))

    else:

        cursor.execute("""
        UPDATE Cart
        SET quantity = ?
        WHERE id = ?
        """, (quantity, item_id))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Cart updated successfully"
    })


# ---------------- DELETE CART ITEM ----------------
@app.route("/api/cart/<int:item_id>", methods=["DELETE"])
def delete_cart_item(item_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM Cart
    WHERE id = ?
    """, (item_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Item removed from cart"
    })


# ---------------- CHECKOUT ----------------
@app.route("/api/checkout", methods=["POST"])
def checkout():

    conn = get_db()
    cursor = conn.cursor()

    # GET ALL CART ITEMS
    cursor.execute("SELECT * FROM Cart")
    items = cursor.fetchall()

    # MOVE ITEMS TO ORDERS TABLE
    for item in items:

        cursor.execute("""
        INSERT INTO Orders (product_name, quantity)
        VALUES (?, ?)
        """, (
            item["product_name"],
            item["quantity"]
        ))

    # CLEAR CART
    cursor.execute("DELETE FROM Cart")

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Order placed successfully"
    })


# ---------------- GET ORDERS ----------------
@app.route("/api/orders", methods=["GET"])
def get_orders():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Orders")
    orders = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in orders])


# ---------------- RUN APP ----------------
if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )