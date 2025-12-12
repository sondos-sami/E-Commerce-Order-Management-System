
from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)
orders_db = {}

def validate_order_data(data):

    errors = []


    if not data:
        return False, ["No data provided"]

    # Validate customer_id
    if "customer_id" not in data:
        errors.append("customer_id is required")
    elif not isinstance(data["customer_id"], int) or data["customer_id"] <= 0:
        errors.append("customer_id must be a positive integer")

    # Validate products
    if "products" not in data:
        errors.append("products array is required")
    elif not isinstance(data["products"], list) or len(data["products"]) == 0:
        errors.append("products must be a non-empty array")
    else:
        for idx, product in enumerate(data["products"]):
            if not isinstance(product, dict):
                errors.append(f"Product at index {idx} must be an object")
                continue

            if "product_id" not in product:
                errors.append(f"Product at index {idx} missing product_id")
            elif not isinstance(product["product_id"], int) or product["product_id"] <= 0:
                errors.append(f"Product at index {idx} has invalid product_id")

            if "quantity" not in product:
                errors.append(f"Product at index {idx} missing quantity")
            elif not isinstance(product["quantity"], int) or product["quantity"] <= 0:
                errors.append(f"Product at index {idx} has invalid quantity")

    # Validate total_amount
    if "total_amount" not in data:
        errors.append("total_amount is required")
    elif not isinstance(data["total_amount"], (int, float)) or data["total_amount"] <= 0:
        errors.append("total_amount must be a positive number")

    return len(errors) == 0, errors


@app.get("/")
def home():
    """Health check endpoint"""
    return jsonify({
        "message": "order_service is running",
        "service": "Order Service",
        "version": "1.0"
    })


@app.get("/test")
def test():
    """Test endpoint"""
    return jsonify({"status": "service running"})


@app.post("/api/orders/create")
def create_order():
    """Create a new order safely"""
    # Parse incoming JSON data safely
    data = request.get_json(silent=True)  # Returns None instead of raising error

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid or missing JSON data"
        }), 400

    # Validate input
    is_valid, errors = validate_order_data(data)
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": "Validation failed",
            "errors": errors
        }), 400

    # Generate unique order ID and timestamp
    order_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    # Create order object
    order = {
        "order_id": order_id,
        "customer_id": data["customer_id"],
        "products": data["products"],
        "total_amount": data["total_amount"],
        "status": "confirmed",
        "created_at": timestamp,
        "updated_at": timestamp
    }

    # Store order in database
    orders_db[order_id] = order

    # Return order confirmation
    return jsonify({
        "status": "success",
        "message": "Order created successfully",
        "order": {
            "order_id": order_id,
            "customer_id": order["customer_id"],
            "total_amount": order["total_amount"],
            "status": order["status"],
            "created_at": timestamp,
            "product_count": len(order["products"])
        }
    }), 201


@app.get("/api/orders/<order_id>")
def get_order(order_id):
    """Retrieve order details by order ID"""
    try:
        # Check if order exists
        if order_id not in orders_db:
            return jsonify({
                "status": "error",
                "message": f"Order with ID {order_id} not found"
            }), 404

        # Retrieve order
        order = orders_db[order_id]

        return jsonify({
            "status": "success",
            "order": order
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while retrieving the order",
            "error": str(e)
        }), 500


@app.get("/api/orders")
def get_all_orders():
    """Get all orders (useful for testing)"""
    try:
        return jsonify({
            "status": "success",
            "total_orders": len(orders_db),
            "orders": list(orders_db.values())
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while retrieving orders",
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "status": "error",
        "message": "Method not allowed"
    }),


if __name__ == "__main__":
    app.run(port=5001, debug=True)