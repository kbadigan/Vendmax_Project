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
# Feature 6: Update product details
@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    if request.method == 'GET':
        # Retrieve the current details of the product
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
            product = cursor.fetchone()

        return render_template('update_product.html', product=product)

    elif request.method == 'POST':
        # Update the specified attributes of the product in the database
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            update_data = {}
            new_name = request.form.get('new_name')
            if new_name:
                update_data['name'] = new_name

            new_price = request.form.get('new_price')
            if new_price is not None:
                update_data['price'] = float(new_price)

            new_stock = request.form.get('new_stock')
            if new_stock is not None:
                update_data['stock'] = int(new_stock)

            # Construct the SET clause based on the provided attributes
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])

            # Update the product in the database
            cursor.execute(f"UPDATE products SET {set_clause} WHERE id=?", (*update_data.values(), product_id))
            conn.commit()

        return redirect(url_for('index'))
@app.route('/transactions')
def transactions():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
    return render_template('transactions_page.html', transactions=transactions)

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
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + search_term + '%',))
            search_results = cursor.fetchall()

        return render_template('search_results.html', search_results=search_results, search_term=search_term)

    return render_template('search.html')
@app.route('/update', methods=['GET', 'POST'])
def update_page():
    if request.method == 'GET':
        # Retrieve the list of products for updating
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

        return render_template('update_page.html', products=products)

    elif request.method == 'POST':
        # Handle the update form submission
        product_id = int(request.form.get('product_id'))

        # Redirect to the specific update page for the selected product
        return redirect(url_for('update_product', product_id=product_id))
@app.route('/transactions')
def transactions_page():
    # Retrieve the transaction history from the database
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()

    return render_template('transactions_page.html', transactions=transactions)
if __name__ == '__main__':
    app.run(debug=True)
