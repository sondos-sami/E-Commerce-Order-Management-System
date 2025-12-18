import sys
import os
from flask import Flask, request, jsonify
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.db_helper import DatabaseManager

app = Flask(__name__)
db_manager = DatabaseManager()

@app.get("/api/products")
def get_all_products():
    db = db_manager.get_connection()
    if not db :
        return jsonify({
            "status": "error", 
            "message": "Database connection failed"
            }), 500
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory")
    products = cursor.fetchall()

    cursor.close()
    db.close()
    return jsonify({
        "status": "success",
        "total_products": len(products),
        "products": products
    })


def validate_product_data(data):
    errors = []

    
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
    db = db_manager.get_connection()
    if not db:
        return jsonify({
            "status": "error",
            "message": "Database connection error"
        }), 500

    try:
        cursor = db.cursor(dictionary=True)

        query = """INSERT INTO inventory (product_name, unit_price, quantity_available ) 
            VALUES (%s, %s, %s)"""
        
        values = (data["name"], data["price"], data["quantity"])
        cursor.execute(query, values)
        db.commit()
        new_id = cursor.lastrowid
        return jsonify({
            "status": "success",
            "message": "Product added successfully",
            "product_id" : new_id,
            "name" : data["name"],
            "price" : data["price"],
            "quantity" : data["quantity"],
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Database operation failed",
            "error": str(e)
        }), 500
    finally:
        cursor.close()
        db.close()

    



@app.put("/api/products/edit/<int:product_id>")
def edit_product(product_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid Json data"
        }), 400
    
    db = db_manager.get_connection()
    if not db:
        return jsonify({
            "status": "error",
            "message": "Database connection error"
        }), 500
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventory WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

    
        if not product:
            return jsonify({
            "status": "error",
            "message": f"Product with ID {product_id} not found"
        }), 404
    
    
        current_name = product["product_name"]
        current_price = product["unit_price"]
        current_qty = product["quantity_available"]


        if "name" in data:
            current_name = data["name"]
        
        if "price" in data:
            if isinstance(data["price"], (int, float)) and data["price"] > 0:
                current_price = data["price"]
            else:
                return jsonify({
                    "status": "error",
                    "message": "price must be a positive number"
                }), 400
            
        if "quantity" in data:
            if isinstance(data["quantity"], (int)) and data["quantity"] >= 0:
                current_qty = data["quantity"]
            else:
                return jsonify({
                    "status": "error",
                    "message": "quantity must be a non-negative integer"
                }), 400
            

        query = """UPDATE inventory 
            SET product_name = %s, unit_price = %s, quantity_available = %s
            WHERE product_id = %s"""
        
        cursor.execute(query, (current_name, current_price, current_qty, product_id))
        db.commit()
        return jsonify({
            "status": "success",
            "message": "Product updated successfully",
            "product": {
                "product_id": product_id,
                "name": current_name,
                "price": float(current_price),
                "quantity": current_qty
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Database operation failed",
            "error": str(e)
        }), 500
    finally:
        cursor.close()
        db.close()


@app.delete("/api/products/delete/<int:product_id>")
def delete_product(product_id):
    db = db_manager.get_connection()

    if not db:
        return jsonify({
            "status": "error",
            "message": "Database connection error"
        }), 500
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventory WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            return jsonify({
                "status": "error",
                "message": f"product with ID {product_id} not found"
            }), 404
        
        cursor.execute("DELETE FROM inventory WHERE product_id = %s", (product_id,))
        db.commit()

        return jsonify({
            "status": "success",
            "message": f"product with ID {product_id} deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Database operation failed",
            "error": str(e)
        }), 500
    finally:
        cursor.close()
        db.close()

@app.get("/api/inventory/check/<int:product_id>")
def check_inventory(product_id):
    db = db_manager.get_connection()
    if not db:
        return jsonify({
            "status": "error",
            "message": "Database connection error"
        }), 500
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT quantity_available FROM inventory WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({
                "status": "error",
                "message": f"product with ID {product_id} not found in the inventory"
            }), 404
        
        return jsonify({
            "status": "success",
            "product_id": product_id,
            "quantity": product["quantity_available"]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Database operation failed",
            "error": str(e)
        }), 500
    finally:
        cursor.close()
        db.close()


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
        
    
    db = db_manager.get_connection()

    if not db:
        return jsonify({
            "status": "error",
            "message": "Database connection error"
        }), 500
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT quantity_available FROM inventory WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({
                "status": "error",
                "message": f"product with ID {product_id} not found"
            }), 404
    

        curur_qty = product["quantity_available"]
        if curur_qty < qty:
            return jsonify({
                "status": "error",
                "message": "insufficient stock"
            }), 400
        new_qty = curur_qty - qty

        cursor.execute("UPDATE inventory SET quantity_available = %s WHERE product_id = %s", (new_qty, product_id,))
        db.commit()
        

        return jsonify({
                "status": "success",
                "message": "inventory updated successfully",
                "product_id": product_id,
                "updated_quantity": new_qty
            }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Database operation failed",
            "error": str(e)
        }), 500
    finally:
        cursor.close()
        db.close()

@app.get("/")
def home():
    return {"message": "inventory_service is running"}

@app.get("/test")
def test():
    return {"status": "service running"}





if __name__ == "__main__":
    app.run(port=5002, debug=True)
