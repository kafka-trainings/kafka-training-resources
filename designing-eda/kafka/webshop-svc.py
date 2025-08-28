from flask import Flask, jsonify
import sqlite3
import json
import threading
from confluent_kafka import Consumer
from config import WEBSHOP_SERVICE_PORT, KAFKA_BOOTSTRAP_SERVERS, PRODUCT_TOPIC, PRICE_TOPIC, INVENTORY_TOPIC

app = Flask(__name__)
app.config['DATABASE'] = 'webshop.db'

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, description TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS prices (product_id INTEGER PRIMARY KEY, price REAL)')
        db.execute('CREATE TABLE IF NOT EXISTS inventory (product_id INTEGER PRIMARY KEY, amount INTEGER, warehouse TEXT)')

def consume_events():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'webshop-service',
        'auto.offset.reset': 'earliest'
    })
    
    consumer.subscribe([PRODUCT_TOPIC, PRICE_TOPIC, INVENTORY_TOPIC])
    
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
            
        topic = msg.topic()
        data = json.loads(msg.value().decode('utf-8'))
        
        with get_db() as db:
            if topic == PRODUCT_TOPIC:
                # Only store fields needed for webshop (no internal_sku)
                db.execute(
                    'INSERT OR REPLACE INTO products (id, name, description) VALUES (?, ?, ?)',
                    (data['id'], data['name'], data['description'])
                )
            elif topic == PRICE_TOPIC:
                db.execute(
                    'INSERT OR REPLACE INTO prices (product_id, price) VALUES (?, ?)',
                    (data['product_id'], data['price'])
                )
            elif topic == INVENTORY_TOPIC:
                db.execute(
                    'INSERT OR REPLACE INTO inventory (product_id, amount, warehouse) VALUES (?, ?, ?)',
                    (data['product_id'], data['amount'], data['warehouse'])
                )

@app.route('/products')
def get_products():
    with get_db() as db:
        products = []
        for row in db.execute('''
            SELECT p.id, p.name, p.description, pr.price,
                   CASE 
                     WHEN SUM(i.amount) IS NULL THEN NULL
                     WHEN SUM(i.amount) > 3 THEN 1
                     ELSE 0
                   END as available
            FROM products p 
            LEFT JOIN prices pr ON p.id = pr.product_id
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id, p.name, p.description, pr.price
        '''):
            product = dict(row)
            # Convert 1/0/None to True/False/None
            if product['available'] is None:
                product['available'] = None
            else:
                product['available'] = bool(product['available'])
            products.append(product)
    return jsonify(products)

@app.route('/products/<int:product_id>')
def get_product(product_id):
    with get_db() as db:
        row = db.execute('''
            SELECT p.id, p.name, p.description, pr.price,
                   CASE 
                     WHEN SUM(i.amount) IS NULL THEN NULL
                     WHEN SUM(i.amount) > 3 THEN 1
                     ELSE 0
                   END as available
            FROM products p 
            LEFT JOIN prices pr ON p.id = pr.product_id 
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.id = ?
            GROUP BY p.id, p.name, p.description, pr.price
        ''', (product_id,)).fetchone()
        if not row:
            return ('', 404)
        product = dict(row)
        # Convert 1/0/None to True/False/None
        if product['available'] is None:
            product['available'] = None
        else:
            product['available'] = bool(product['available'])
    return jsonify(product)

if __name__ == '__main__':
    init_db()
    
    # Start Kafka consumer in background thread
    consumer_thread = threading.Thread(target=consume_events, daemon=True)
    consumer_thread.start()
    
    app.run(debug=True, port=WEBSHOP_SERVICE_PORT)