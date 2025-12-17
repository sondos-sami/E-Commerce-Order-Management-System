from flask import Flask, jsonify, request

app = Flask(__name__)

# --- (Mock Customer DB) ---
customers_db = {
    1: {
        "customer_id": 1,
        "name": "Fatemah Atef ",
        "email": "Fatema@example.com",
        "phone": "01012345678",
        "loyalty_points": 100
    },
    2: {
        "customer_id": 2,
        "name": "Sara Mohamed",
        "email": "sara@example.com",
        "phone": "01098765432",
        "loyalty_points": 250
    }
}

@app.get("/api/customers/<int:customer_id>")
def get_customer(customer_id):
    customer = customers_db.get(customer_id)
    if customer:
        return jsonify({
            "status": "success",
            "customer": customer
        }), 200
    return jsonify({"status": "error", "message": "Customer not found"}), 404

@app.put("/api/customers/<int:customer_id>/loyalty")
def update_loyalty(customer_id):
    data = request.get_json(silent=True)
    if not data or "points" not in data:
        return jsonify({"status": "error", "message": "Points value is required"}), 400
    
    if customer_id in customers_db:
        customers_db[customer_id]["loyalty_points"] += data["points"]
        return jsonify({
            "status": "success", 
            "message": "Loyalty points updated",
            "new_balance": customers_db[customer_id]["loyalty_points"]
        }), 200
    return jsonify({"status": "error", "message": "Customer not found"}), 404

if __name__ == "__main__":
    app.run(port=5004, debug=True)