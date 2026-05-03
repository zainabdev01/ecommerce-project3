from flask import Flask, request, jsonify
import pyodbc
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==============================
# SQL SERVER CONNECTION
# ==============================
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Ecommerce_order_managmentsystem;'
    'Trusted_Connection=yes;'
)

# ==============================
# HOME TEST
# ==============================
@app.route('/')
def home():
    return "Ecommerce Backend is Running"

# ==============================
# PRODUCTS API
# ==============================
@app.route('/products', methods=['GET'])
def products():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    
    data = []
    for row in cursor.fetchall():
        data.append({
            "id": row.product_id,
            "name": row.name,
            "price": float(row.price),
            "stock": row.stock_quantity
        })
    return jsonify(data)

# ==============================
# USERS API
# ==============================
@app.route('/users', methods=['GET'])
def users():
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email FROM Users")

    data = []
    for row in cursor.fetchall():
        data.append({
            "id": row.user_id,
            "name": row.name,
            "email": row.email
        })
    return jsonify(data)

# ==============================
# ORDERS API
# ==============================
@app.route('/orders/<int:user_id>', methods=['GET'])
def orders(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE user_id = ?", (user_id,))

    data = []
    for row in cursor.fetchall():
        data.append({
            "order_id": row.order_id,
            "status": row.status
        })
    return jsonify(data)

# ==============================
# RUN SERVER
# ==============================
if __name__ == '__main__':
    app.run(debug=True)