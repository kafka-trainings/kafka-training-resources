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
        db.execute('CREATE TABLE IF NOT EXISTS prices (product_id INTEGER PRIMARY KEY, price REAL)')
        prices = [
            (1, 999.99),
            (2, 29.99),
            (3, 149.99)
        ]
        db.executemany('INSERT OR IGNORE INTO prices VALUES (?, ?)', prices)
        
        # Publish initial prices to Kafka
        for p in prices:
            event = {'product_id': p[0], 'price': p[1], 'action': 'created'}
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
        db.execute('INSERT OR REPLACE INTO prices (product_id, price) VALUES (?, ?)', 
                  (data['product_id'], data['price']))
    
    # Publish to Kafka
    event = {'product_id': data['product_id'], 'price': data['price'], 'action': 'updated'}
    producer.produce(PRICE_TOPIC, key=str(data['product_id']), value=json.dumps(event))
    producer.flush()
    
    return jsonify(data), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRICE_SERVICE_PORT)