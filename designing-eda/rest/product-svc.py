from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
from config import PRODUCT_SERVICE_PORT

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'rest_products_db',
    'user': 'user',
    'password': 'password'
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name VARCHAR(255), description TEXT, internal_sku VARCHAR(255))')
            products = [
                ('Laptop', 'Gaming laptop', 'INT-LAP-001'),
                ('Mouse', 'Wireless mouse', 'INT-MOU-002'), 
                ('Keyboard', 'Mechanical keyboard', 'INT-KEY-003')
            ]
            for p in products:
                cur.execute('''INSERT INTO products (name, description, internal_sku) 
                              VALUES (%s, %s, %s)''', p)

@app.route('/products')
def get_products():
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM products')
            return jsonify([dict(row) for row in cur.fetchall()])

@app.route('/products/<int:id>')
def get_product(id):
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM products WHERE id = %s', (id,))
            row = cur.fetchone()
            return jsonify(dict(row)) if row else ('', 404)

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('INSERT INTO products (name, description, internal_sku) VALUES (%s, %s, %s) RETURNING id', 
                       (data['name'], data.get('description', ''), data.get('internal_sku', '')))
            row = cur.fetchone()
            id = row['id']
    return jsonify({'id': id, **data}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRODUCT_SERVICE_PORT)