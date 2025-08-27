from flask import Flask, request, jsonify
import sqlite3
import time
from config import PRICE_SERVICE_PORT

app = Flask(__name__)
app.config['DATABASE'] = 'prices.db'

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute('CREATE TABLE IF NOT EXISTS prices (product_id INTEGER PRIMARY KEY, price REAL)')
        db.executemany('INSERT OR IGNORE INTO prices VALUES (?, ?)', [
            (1, 999.99),
            (2, 29.99),
            (3, 149.99)
        ])

@app.route('/prices')
def get_prices():
    time.sleep(1) # Calculate price using black magic
    return jsonify([dict(row) for row in get_db().execute('SELECT * FROM prices')])

@app.route('/prices/<int:product_id>')
def get_price(product_id):
    time.sleep(1) # Calculate price using black magic
    row = get_db().execute('SELECT * FROM prices WHERE product_id = ?', (product_id,)).fetchone()
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