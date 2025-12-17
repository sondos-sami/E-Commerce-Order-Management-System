from flask import Flask,request, jsonify
from datetime import datetime 

app = Flask(__name__)
inventory_dp = {
    1: {
        "product_id": 1,
        "name": "Laptop",
        "price": 1000,
        "quantity": 10,
        "last_updated": datetime.now().isoformat()
    },
    2: {
        "product_id": 2,
        "name": "Mouse",
        "price": 20,
        "quantity": 50,
        "last_updated": datetime.now().isoformat()
    },
    3: {
        "product_id": 3,
        "name": "Keyboard",
        "price": 30,
        "quantity": 30,
        "last_updated": datetime.now().isoformat()
    }
}

@app.get("/api/products")
def get_all_products():
    return jsonify({
        "status": "success",
        "total_products": len(inventory_dp),
        "products": list(inventory_dp.values())
    })


@app.get("/api/products/<int:product_id>")
def get_product_by_id(product_id):
    product = inventory_dp.get(product_id)
    if not product:
        return jsonify({
            "status": "error",
            "message": "Product not found"
        }),404
    return jsonify({
        "status": "success",
        "product": product
    })


def validate_product_data(data):
    errors = []

    if "product_id" not in data or not isinstance(data["product_id"], int):
        errors.append("Product_id is required and must be an integer")
    
    if "name" not in data or not isinstance(data["name"], str):
        errors.append("Name is required and must be a string")

    if "price" not in data or not isinstance(data["price"], float) or data["price"] <= 0:
        errors.append("price is required and must be a positive number")

    if "quantity" not in data or not isinstance(data["quantity"], int) or data["quantity"] <= 0:
        errors.append("quantity is required and must be a non-negative integer")

    return len(errors) == 0, errors


@app.post("/api/products/add")
def add_product():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid Json data"
        }), 400
    
    is_valid, errors = validate_product_data(data)

    if not is_valid:
        return jsonify({
            "status": "error",
            "message": "Validation error",
            "error": errors
        }), 404
    
    prduct_id = data["product_id"]

    if prduct_id in inventory_dp:
        return jsonify({
            "status": "error",
            "message": f"Product with ID {prduct_id} already exists"
        }), 404
    
    inventory_dp[prduct_id] = {
        "product_id" : prduct_id,
        "name" : data["name"],
        "price" : data["price"],
        "quantity" : data["quantity"],
        "last_updated": datetime.now().isoformat()

    }

    return jsonify({
        "status": "success",
        "message": "Product added successfully",
        "product": inventory_dp[prduct_id]
    }), 201


@app.put("/api/products/edit/<int:product_id>")
def edit_product(product_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid Json data"
        }), 400
    
    if product_id not in inventory_dp:
        return jsonify({
            "status": "error",
            "message": f"Product with ID {product_id} not found"
        }), 404
    
    product = inventory_dp[product_id]

    if "name" in data:
        product["name"] = data["name"]
    
    if "price" in data:
        if isinstance(data["price"], (int, float)) and data["price"] > 0:
            product["price"] = data["price"]
        else:
            return jsonify({
                 "status": "error",
                 "message": "price must be a positive number"
            }), 400
        
    if "quantity" in data:
        if isinstance(data["quantity"], (int)) and data["quantity"] >= 0:
            product["quantity"] = data["quantity"]
        else:
            return jsonify({
                 "status": "error",
                 "message": "quantity must be a non-negative integer"
            }), 400
        
    product["last_updated"] = datetime.now().isoformat()
    return jsonify({
        "status": "success",
        "message": "Product updated successfully",
        "product": product
    }), 200


@app.delete("/api/products/delete/<int:product_id>")
def delete_product(product_id):
    if product_id not in inventory_dp:
        return jsonify({
            "status": "error",
            "message": f"product with ID {product_id} not found"
        }), 404
    
    deleted_product = inventory_dp.pop(product_id)

    return jsonify({
        "status": "success",
        "message": f"product with ID {product_id} deleted successfully"
    }), 200


@app.get("/api/inventory/check/<int:product_id>")
def check_inventory(product_id):
    product = inventory_dp.get(product_id)

    if not product:
        return jsonify({
            "status": "error",
            "message": f"product with ID {product_id} not found in the inventory"
        }), 404
    
    return jsonify({
        "status": "success",
        "product id": product_id,
        "quntity": product["quantity"] 
    }), 200


@app.put("/api/inventory/update")
def update_inventory():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid Json data"
        }), 400
    
    product_id = data.get("product_id")
    qty = data.get("quantity")

    if not isinstance(product_id, int) or not isinstance(qty, int) or qty <= 0:
        return jsonify({
            "status": "error",
            "message": "product id and quantity must be positive integer"
        }), 400
    
    product = inventory_dp.get(product_id)

    if not product:
        return jsonify({
            "status": "error",
            "message": "product not found"
        }), 404
    
    if product["quantity"] < qty:
        return jsonify({
            "status": "error",
            "message": "insufficient stock"
        }), 400
    
    product["quantity"] -= qty
    product["last_updated"] = datetime.now().isoformat()

    return jsonify({
            "status": "success",
            "message": "inventory updated successfully",
            "product": product
        }), 200

@app.get("/")
def home():
    return {"message": "inventory_service is running"}

@app.get("/test")
def test():
    return {"status": "service running"}





if __name__ == "__main__":
    app.run(port=5002, debug=True)
