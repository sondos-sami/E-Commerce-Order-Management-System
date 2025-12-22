import sys
import os
from flask import Flask, request, jsonify
from datetime import datetime
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.db_helper import DatabaseManager

app = Flask(__name__)
db_manager = DatabaseManager()

@app.post("/api/orders/create")
def create_order():
    data = request.get_json()
    order_id = str(uuid.uuid4())

    db = db_manager.get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO orders (order_id, customer_id, total_amount, status, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        order_id,
        data["customer_id"],
        data["total_amount"],
        "confirmed",
        datetime.utcnow()
    ))

    for item in data["products"]:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (
            order_id,
            item["product_id"],
            item["quantity"]
        ))

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"order_id": order_id}), 201

@app.get("/")
def home():
    return {"message": "order_service running"}

if __name__ == "__main__":
    app.run(port=5001, debug=True)