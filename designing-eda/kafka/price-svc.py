from flask import Flask, request, jsonify
import sqlite3
import json
import time
from confluent_kafka import Producer
from config import PRICE_SERVICE_PORT, KAFKA_BOOTSTRAP_SERVERS, PRICE_TOPIC

app = Flask(__name__)
app.config['DATABASE'] = 'prices.db'

producer = Producer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'partitioner': 'murmur2_random'})

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER, 
            price REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        prices = [
            (1, 999.99),
            (2, 29.99),
            (3, 149.99)
        ]
        for p in prices:
            db.execute('INSERT OR IGNORE INTO prices (product_id, price) VALUES (?, ?)', p)
        
        # Publish initial prices to Kafka (get timestamps from DB)
        for row in db.execute('SELECT * FROM prices'):
            event = {
                'product_id': row['product_id'], 
                'price': row['price'], 
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'action': 'created'
            }
            producer.produce(PRICE_TOPIC, json.dumps(event))
        producer.flush()

@app.route('/prices')
def get_prices():
    return jsonify([dict(row) for row in get_db().execute('SELECT * FROM prices')])

@app.route('/prices/<int:product_id>')
def get_price(product_id):
    time.sleep(1)
    row = get_db().execute('SELECT * FROM prices WHERE product_id = ?', (product_id,)).fetchone()
    return jsonify(dict(row)) if row else ('', 404)

@app.route('/prices', methods=['POST'])
def create_price():
    time.sleep(1) # Calculate price using black magic
    data = request.json
    
    with get_db() as db:
        # Insert new price - id is auto-generated
        id = db.execute('INSERT INTO prices (product_id, price) VALUES (?, ?)', 
                       (data['product_id'], data['price'])).lastrowid
        
        # Get the inserted row with all fields
        row = db.execute('SELECT * FROM prices WHERE id = ?', (id,)).fetchone()
    
    # Publish to Kafka
    event = {
        'id': row['id'],
        'product_id': row['product_id'], 
        'price': row['price'], 
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
        'action': 'created'
    }
    producer.produce(PRICE_TOPIC, key=str(row['product_id']), value=json.dumps(event))
    producer.flush()
    
    return jsonify(dict(row)), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRICE_SERVICE_PORT)