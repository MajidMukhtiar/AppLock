from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DB_NAME = "redoAgain.db"

# 📌 Ensure database and tables are created
def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 🚗 Cars Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        image_url TEXT NOT NULL,
        description TEXT
    )
    """)

    # 🛒 Cart Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
    )
    """)

    # 🛍 Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        total_price REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        car_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# 🔗 Get Database Connection
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # ✅ Enforce foreign key constraints
    return conn

# 📌 Initialize the database before starting the app
initialize_db()

# 🏠 Home Page
@app.route("/")
def home():
    return render_template("redo.html")

# 🚗 Get all cars
@app.route("/get_cars", methods=["GET"])
def get_cars():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cars")
        cars = cursor.fetchall()
        conn.close()

        # Convert to list of dictionaries
        car_list = [
            {
                "id": car[0],
                "name": car[1],
                "price": car[2],
                "image_url": car[3],
                "description": car[4]
            }
            for car in cars
        ]
        
        return jsonify({"cars": car_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a single car

@app.route("/admin", methods=["GET"])
def admin_panel():
    return render_template("admin.html")

@app.route("/admin/add_car", methods=["POST"])
def add_car():
    try:
        data = request.get_json()  # Get JSON data
        
        # Validate input
        required_fields = ["name", "price", "image_url", "description"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert a single car
        cursor.execute(
            "INSERT INTO cars (name, price, image_url, description) VALUES (?, ?, ?, ?)",
            (data["name"], data["price"], data["image_url"], data["description"])
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Car added successfully!"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add multiple cars (Optional)

@app.route("/admin/delete_car", methods=["POST"])
def delete_car():
    try:
        data = request.get_json()  # Get JSON data

        car_id = data.get("id")
        car_name = data.get("name")

        if not car_id and not car_name:
            return jsonify({"error": "Either ID or Name is required!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        if car_id:
            cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
        elif car_name:
            cursor.execute("DELETE FROM cars WHERE name = ?", (car_name,))

        if cursor.rowcount == 0:
            return jsonify({"error": "Car not found!"}), 404

        conn.commit()
        conn.close()

        return jsonify({"message": "Car deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/admin/update_car", methods=["POST"])
def update_car():
    try:
        data = request.get_json()  # Get JSON data

        car_id = data.get("id")
        car_name = data.get("name")

        if not car_id and not car_name:
            return jsonify({"error": "Car ID or Name is required!"}), 400

        update_fields = []
        update_values = []

        if "new_name" in data and data["new_name"]:
            update_fields.append("name = ?")
            update_values.append(data["new_name"])

        if "price" in data and data["price"]:
            update_fields.append("price = ?")
            update_values.append(data["price"])

        if "image_url" in data and data["image_url"]:
            update_fields.append("image_url = ?")
            update_values.append(data["image_url"])

        if "description" in data and data["description"]:
            update_fields.append("description = ?")
            update_values.append(data["description"])

        if not update_fields:
            return jsonify({"error": "No update fields provided!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        if car_id:
            query = f"UPDATE cars SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(car_id)
        else:
            query = f"UPDATE cars SET {', '.join(update_fields)} WHERE name = ?"
            update_values.append(car_name)

        cursor.execute(query, update_values)

        if cursor.rowcount == 0:
            return jsonify({"error": "Car not found!"}), 404

        conn.commit()
        conn.close()

        return jsonify({"message": "Car updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add_cars", methods=["POST"])
def add_cars():
    try:
        data = request.get_json()

        if not isinstance(data, list) or not data:
            return jsonify({"error": "Invalid data format. Expected a list of cars."}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert multiple cars
        cursor.executemany(
            "INSERT INTO cars (name, price, image_url, description) VALUES (?, ?, ?, ?)",
            [(car["name"], car["price"], car["image_url"], car.get("description", "")) for car in data]
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Cars added successfully!"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add_to_cart/<int:car_id>", methods=["POST"])
def add_to_cart(car_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if car exists
        cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
        car = cursor.fetchone()
        if not car:
            return jsonify({"error": "Car not found"}), 404  # ✅ Handle invalid car_id

        # Check if car is in cart
        cursor.execute("SELECT * FROM cart WHERE car_id = ?", (car_id,))
        existing_item = cursor.fetchone()

        if existing_item:
            # Increase quantity
            cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE car_id = ?", (car_id,))
        else:
            # Add new item to cart
            cursor.execute("INSERT INTO cart (car_id, quantity) VALUES (?, 1)", (car_id,))

        conn.commit()
        conn.close()
        return jsonify({"message": "Car added to cart!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500# 🛒 Get Cart Items
@app.route("/cart", methods=["GET"])
def view_cart():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch cart items with car details
    cursor.execute("""
        SELECT cars.id, cars.name, cars.price, cars.image_url, cart.quantity
        FROM cart
        JOIN cars ON cart.car_id = cars.id
    """)
    cart_items = cursor.fetchall()
    conn.close()

    # Convert to JSON format & Calculate Total Price
    total_price = sum(item[2] * item[4] for item in cart_items)  # price * quantity

    cart_list = [
        {
            "id": item[0],
            "name": item[1],
            "price": item[2],
            "image_url": item[3],
            "quantity": item[4]
        }
        for item in cart_items
    ]

    return render_template("cart.html", cart_items=cart_list, total_price=total_price)

@app.route("/place_order", methods=["GET"])
def place_order():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch cart items with car details
    cursor.execute("""
        SELECT cars.id, cars.name, cars.price, cars.image_url, cart.quantity
        FROM cart
        JOIN cars ON cart.car_id = cars.id
    """)
    cart_items = cursor.fetchall()

    # Calculate total price
    total_price = sum(item[2] * item[4] for item in cart_items)

    conn.close()

    return render_template("place_order_receipt.html", cart_items=cart_items, total_price=total_price)

@app.route("/submit_order", methods=["POST"])
def submit_order():
    try:
        data = request.get_json()  # ✅ JSON ڈیٹا لوڈ کریں

        name = data.get("name")
        email = data.get("email")
        address = data.get("address")

        # ✅ Validate inputs
        if not name or not email or not address:
            return jsonify({"error": "All fields are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Fetch cart items & total price
        cursor.execute("""
            SELECT SUM(cars.price * cart.quantity) 
            FROM cart 
            JOIN cars ON cart.car_id = cars.id
        """)
        total_price = cursor.fetchone()[0]

        if total_price is None:
            return jsonify({"error": "Cart is empty"}), 400  # ✅ Cart خالی ہونے پر Error Handle کریں

        # ✅ Insert order into database
        cursor.execute(
            "INSERT INTO orders (name, email, address, total_price) VALUES (?, ?, ?, ?)",
            (name, email, address, total_price),
        )

        # ✅ Clear cart after successful order placement
        cursor.execute("DELETE FROM cart")
        conn.commit()
        conn.close()

        return jsonify({"message": "Order placed successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
 # kam ka hai yeh ------------------------------------------------------------------ nechay wala   
# @app.route("/orders", methods=["GET"])
# def orders_page():
#     return render_template("orders.html")  # Renders the HTML page

# @app.route("/get_orders", methods=["GET"])
# def get_orders():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM orders")
#     orders = cursor.fetchall()
#     conn.close()

#     order_list = [
#         {"id": order[0], "name": order[1], "email": order[2], "address": order[3], "total_price": order[4]}
#         for order in orders
#     ]

#     return jsonify({"orders": order_list})  # Returns orders as JSON ----------------------


@app.route("/orders", methods=["GET"])
def orders_page():
    return render_template("orders.html")  # Renders the orders page

@app.route("/get_orders", methods=["GET"])
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()

    order_list = [
        {"id": order["id"], "name": order["name"], "email": order["email"], "address": order["address"], "total_price": order["total_price"]}
        for order in orders
    ]
    
    return jsonify({"orders": order_list})

@app.route("/total_sales", methods=["GET"])
def total_sales():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(total_price), 0) FROM orders")  # Ensure it never returns None
    total_sales = cursor.fetchone()[0]
    conn.close()
    return jsonify({"total_sales": float(total_sales)})  # Ensure float format

@app.route("/total_orders", methods=["GET"])
def total_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    conn.close()
    return jsonify({"total_orders": total_orders})  # Return count directly

@app.route("/top_orders", methods=["GET"])
def top_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY total_price DESC LIMIT 10")
    top_orders = cursor.fetchall()
    conn.close()

    order_list = [
        {"id": order["id"], "name": order["name"], "email": order["email"], "address": order["address"], "total_price": order["total_price"]}
        for order in top_orders
    ]

    return jsonify({"top_orders": order_list})


# @app.route("/order_operations", methods=["GET"]) 
# def order_opr():
#     return render_template("order_operations.html")  # Displays orders.html

# @app.route("/get_order_opr", methods=["GET"])
# def get_order_opr():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM orders")
#     orders = cursor.fetchall()
#     conn.close()

#     order_list = [
#         {"id": order["order_id"], "name": order["name"], "email": order["email"], 
#          "address": order["address"], "total_price": order["total_amount"]}
#         for order in orders
#     ]

#     return jsonify({"orders": order_list})  # Returns orders as JSON

# @app.route("/total_sales", methods=["GET"])
# def total_sales():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT SUM(total_amount) FROM orders")
#     total_sales = cursor.fetchone()[0]
#     conn.close()

#     return jsonify({"total_sales": total_sales or 0})  # Avoids returning None

# @app.route("/total_orders", methods=["GET"])
# def total_orders():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT COUNT(*) FROM orders")
#     total_orders = cursor.fetchone()[0]
#     conn.close()

#     return jsonify({"total_orders": total_orders})

# @app.route("/top_orders", methods=["GET"])
# def top_orders():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM orders ORDER BY total_amount DESC LIMIT 10")
#     top_orders = cursor.fetchall()
#     conn.close()

#     order_list = [
#         {"id": order["order_id"], "name": order["name"], "email": order["email"], 
#          "address": order["address"], "total_price": order["total_amount"]}
#         for order in top_orders
#     ]

#     return jsonify({"top_orders": order_list})  # Returns top 10 orders




if __name__ == "__main__":
    app.run(debug=True, port=5000)