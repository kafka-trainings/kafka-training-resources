from flask import Flask, jsonify
import psycopg2
import psycopg2.extras
import json
import threading
from confluent_kafka import Consumer
from config import WEBSHOP_SERVICE_PORT, KAFKA_BOOTSTRAP_SERVERS, PRODUCT_TOPIC, PRICE_TOPIC, INVENTORY_TOPIC

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'webshop_db',
    'user': 'user',
    'password': 'password'
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY, 
                name VARCHAR(255), 
                description TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS prices (
                product_id INTEGER PRIMARY KEY, 
                price DECIMAL(10,2),
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS inventory (
                product_id INTEGER PRIMARY KEY, 
                amount INTEGER, 
                warehouse VARCHAR(255),
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )''')

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
            with db.cursor() as cur:
                if topic == PRODUCT_TOPIC:
                    # Only store fields needed for webshop (no internal_sku)
                    cur.execute(
                        '''INSERT INTO products (id, name, description, created_at, updated_at) 
                           VALUES (%s, %s, %s, %s, %s) 
                           ON CONFLICT (id) DO UPDATE SET 
                           name = EXCLUDED.name, 
                           description = EXCLUDED.description,
                           updated_at = EXCLUDED.updated_at''',
                        (data['id'], data['name'], data['description'], 
                         data.get('created_at'), data.get('updated_at'))
                    )
                elif topic == PRICE_TOPIC:
                    cur.execute(
                        '''INSERT INTO prices (product_id, price, created_at, updated_at) 
                           VALUES (%s, %s, %s, %s) 
                           ON CONFLICT (product_id) DO UPDATE SET 
                           price = EXCLUDED.price,
                           updated_at = EXCLUDED.updated_at''',
                        (data['product_id'], data['price'], 
                         data.get('created_at'), data.get('updated_at'))
                    )
                elif topic == INVENTORY_TOPIC:
                    cur.execute(
                        '''INSERT INTO inventory (product_id, amount, warehouse, created_at, updated_at) 
                           VALUES (%s, %s, %s, %s, %s) 
                           ON CONFLICT (product_id) DO UPDATE SET 
                           amount = EXCLUDED.amount,
                           warehouse = EXCLUDED.warehouse,
                           updated_at = EXCLUDED.updated_at''',
                        (data['product_id'], data['amount'], data['warehouse'], 
                         data.get('created_at'), data.get('updated_at'))
                    )

@app.route('/products')
def get_products():
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('''
                SELECT p.id, p.name, p.description, pr.price,
                       CASE 
                         WHEN SUM(i.amount) IS NULL THEN NULL
                         WHEN SUM(i.amount) > 3 THEN true
                         ELSE false
                       END as available
                FROM products p 
                LEFT JOIN prices pr ON p.id = pr.product_id
                LEFT JOIN inventory i ON p.id = i.product_id
                GROUP BY p.id, p.name, p.description, pr.price
            ''')
            products = []
            for row in cur.fetchall():
                product = dict(row)
                # Convert Decimal to float for JSON serialization
                if product['price']:
                    product['price'] = float(product['price'])
                products.append(product)
            return jsonify(products)

@app.route('/products/<int:product_id>')
def get_product(product_id):
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('''
                SELECT p.id, p.name, p.description, pr.price,
                       CASE 
                         WHEN SUM(i.amount) IS NULL THEN NULL
                         WHEN SUM(i.amount) > 3 THEN true
                         ELSE false
                       END as available
                FROM products p 
                LEFT JOIN prices pr ON p.id = pr.product_id 
                LEFT JOIN inventory i ON p.id = i.product_id
                WHERE p.id = %s
                GROUP BY p.id, p.name, p.description, pr.price
            ''', (product_id,))
            row = cur.fetchone()
            if not row:
                return ('', 404)
            product = dict(row)
            # Convert Decimal to float for JSON serialization
            if product['price']:
                product['price'] = float(product['price'])
            return jsonify(product)

if __name__ == '__main__':
    init_db()
    
    # Start Kafka consumer in background thread
    consumer_thread = threading.Thread(target=consume_events, daemon=True)
    consumer_thread.start()
    
    app.run(debug=True, port=WEBSHOP_SERVICE_PORT)