from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import time
from config import PRICE_SERVICE_PORT

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'rest_prices_db',
    'user': 'user',
    'password': 'password'
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS prices (product_id INTEGER PRIMARY KEY, price DECIMAL(10,2))')
            prices = [
                (1, 999.99),
                (2, 29.99),
                (3, 149.99)
            ]
            for p in prices:
                cur.execute('INSERT INTO prices VALUES (%s, %s) ON CONFLICT DO NOTHING', p)

@app.route('/prices')
def get_prices():
    time.sleep(1) # Calculate price using black magic
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM prices')
            return jsonify([dict(row) for row in cur.fetchall()])

@app.route('/prices/<int:product_id>')
def get_price(product_id):
    time.sleep(1) # Calculate price using black magic
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM prices WHERE product_id = %s', (product_id,))
            row = cur.fetchone()
            return jsonify(dict(row)) if row else ('', 404)

@app.route('/prices', methods=['POST'])
def create_price():
    data = request.json
    with get_db() as db:
        db.execute('INSERT OR REPLACE INTO prices (product_id, price) VALUES (?, ?)', 
                  (data['product_id'], data['price']))
    return jsonify(data), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRICE_SERVICE_PORT)