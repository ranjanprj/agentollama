from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "orders.db"

def initialize_db():
    """Initialize the database and create the orders table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_item REAL NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL
                
            )
        ''')
        conn.commit()

@app.route('/orders/get_stock/<string:item_name>/', methods=['GET'])
def get_stock(item_name):
    """Check stock for a specific item."""
    print(item_name)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        sql = f"SELECT * FROM orders"
        cursor.execute(sql)
        print(cursor.fetchone(),'-------')
        cursor.execute('''
            SELECT quantity FROM stock WHERE item_name = ?
        ''', (item_name,))
        row = cursor.fetchone()
        
    if row:
        return jsonify({"stock_quantity": row[0]}), 200
    return jsonify({"stock_exists": "Stock does not exists"}), 200

@app.route('/orders', methods=['POST'])
def add_order():
    """Add a new order."""
    data = request.json
    item_name = data.get('item_name')
    quantity = data.get('quantity')
    price_per_item = data.get('price_per_item')
    print(data)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (item_name, quantity, price_per_item)
            VALUES (?, ?, ?)
        ''', (item_name, quantity, price_per_item))
        conn.commit()
        order_id = cursor.lastrowid

    return jsonify({'order_id': order_id}), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Retrieve an order by ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM orders WHERE id = ?
        ''', (order_id,))
        row = cursor.fetchone()

    if row:
        order = {
            "id": row[0],
            "item_name": row[1],
            "quantity": row[2],
            "price_per_item": row[3]
        }
        return jsonify(order), 200

    return jsonify({"error": "Order not found"}), 404

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order by ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM orders WHERE id = ?
        ''', (order_id,))
        conn.commit()

        if cursor.rowcount > 0:
            return jsonify({"message": "Order deleted"}), 200

    return jsonify({"error": "Order not found"}), 404

# Initialize the database and run the Flask app
if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
