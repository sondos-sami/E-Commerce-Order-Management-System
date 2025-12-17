from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- (Mock Database) ---
PRICING_RULES = [
    {"rule_id": 1, "product_id": 1, "min_quantity": 5, "discount_percentage": 10.00},
    {"rule_id": 2, "product_id": 2, "min_quantity": 10, "discount_percentage": 15.00},
    {"rule_id": 3, "product_id": 3, "min_quantity": 10, "discount_percentage": 12.00},
]

INVENTORY_SERVICE_URL = "http://localhost:5002/api/products"

@app.route('/api/pricing/calculate', methods=['POST'])
def calculate_pricing():
    data = request.get_json(silent=True)
    
    if not data or "products" not in data:
        return jsonify({"status": "error", "message": "Invalid input, 'products' list is required"}), 400

    products_list = data.get("products")
    final_details = []
    total_order_price = 0.0

    try:
        for item in products_list:
            p_id = item.get("product_id")
            qty = item.get("quantity")

            try:
                inv_res = requests.get(f"{INVENTORY_SERVICE_URL}/{p_id}", timeout=2)
                
                if inv_res.status_code == 200:
                    res_json = inv_res.json()
                    product_info = res_json.get("product") 
                    
                    base_price = float(product_info.get("price")) 
                    product_name = product_info.get("name")
                else:
                    return jsonify({
                        "status": "error", 
                        "message": f"Product ID {p_id} not found in inventory"
                    }), 404

            except requests.exceptions.ConnectionError:
                return jsonify({
                    "status": "error", 
                    "message": "Inventory Service is offline. Please start it on port 5002."
                }), 500

            applicable_rules = [
                r for r in PRICING_RULES 
                if r["product_id"] == p_id and qty >= r["min_quantity"]
            ]
            
            if applicable_rules:
                best_rule = max(applicable_rules, key=lambda x: x["min_quantity"])
                discount = float(best_rule["discount_percentage"])
            else:
                discount = 0.0

            subtotal = base_price * qty
            discount_value = subtotal * (discount / 100)
            final_item_price = subtotal - discount_value

            final_details.append({
                "product_id": p_id,
                "name": product_name,
                "base_price": base_price,
                "quantity": qty,
                "discount_applied": f"{discount}%",
                "item_total": round(final_item_price, 2)
            })
            total_order_price += final_item_price

        return jsonify({
            "status": "success",
            "grand_total": round(total_order_price, 2),
            "details": final_details
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5003, debug=True)