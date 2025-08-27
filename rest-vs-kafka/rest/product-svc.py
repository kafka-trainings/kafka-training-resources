from flask import Flask, request, jsonify
import sqlite3
from config import PRODUCT_SERVICE_PORT

app = Flask(__name__)
app.config['DATABASE'] = 'products.db'

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, description TEXT, internal_sku TEXT)')
        db.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)', [
            (1, 'Laptop', 'Gaming laptop', 'INT-LAP-001'),
            (2, 'Mouse', 'Wireless mouse', 'INT-MOU-002'), 
            (3, 'Keyboard', 'Mechanical keyboard', 'INT-KEY-003')
        ])

@app.route('/products')
def get_products():
    return jsonify([dict(row) for row in get_db().execute('SELECT * FROM products')])

@app.route('/products/<int:id>')
def get_product(id):
    row = get_db().execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    return jsonify(dict(row)) if row else ('', 404)

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    with get_db() as db:
        id = db.execute('INSERT INTO products (name, description) VALUES (?, ?)', 
                       (data['name'], data.get('description', ''))).lastrowid
    return jsonify({'id': id, **data}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRODUCT_SERVICE_PORT)