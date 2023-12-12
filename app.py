from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# SQLite database file
DB_FILE = "vendmax.db"

# Create tables if not exist
with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """)
    conn.commit()

@app.route('/')
def index():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form.get('product_name')
    price = float(request.form.get('product_price'))
    stock = int(request.form.get('product_stock'))

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/transactions')
def transactions():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
    return render_template('transactions.html', transactions=transactions)

@app.route('/purchase/<int:product_id>', methods=['POST'])
def purchase(product_id):
    quantity = int(request.form.get('quantity'))

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()

        if product and product[3] >= quantity:  # Check if the product exists and has enough stock
            total_price = product[2] * quantity

            cursor.execute("UPDATE products SET stock=stock-? WHERE id=?", (quantity, product_id))
            cursor.execute("INSERT INTO transactions (product_id, quantity, total_price) VALUES (?, ?, ?)",
                           (product_id, quantity, total_price))
            conn.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
