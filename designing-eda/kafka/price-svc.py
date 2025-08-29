from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import json
import time
from confluent_kafka import Producer
from config import PRICE_SERVICE_PORT, KAFKA_BOOTSTRAP_SERVERS, PRICE_TOPIC

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'prices_db',
    'user': 'user',
    'password': 'password'
}

producer = Producer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'partitioner': 'murmur2_random'})

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS prices (
                id SERIAL PRIMARY KEY,
                product_id INTEGER, 
                price DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            prices = [
                (1, 999.99),
                (2, 29.99),
                (3, 149.99)
            ]
            for p in prices:
                cur.execute('INSERT INTO prices (product_id, price) VALUES (%s, %s) ON CONFLICT DO NOTHING', p)
            
            # Publish initial prices to Kafka (get timestamps from DB)
            cur.execute('SELECT * FROM prices')
            for row in cur.fetchall():
                event = {
                    'id': row[0],
                    'product_id': row[1], 
                    'price': float(row[2]), 
                    'created_at': row[3].isoformat() if row[3] else None,
                    'updated_at': row[4].isoformat() if row[4] else None,
                    'action': 'created'
                }
                producer.produce(PRICE_TOPIC, key=str(row[1]), value=json.dumps(event))
            producer.flush()

@app.route('/prices')
def get_prices():
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM prices')
            return jsonify([dict(row) for row in cur.fetchall()])

@app.route('/prices/<int:product_id>')
def get_price(product_id):
    time.sleep(1)
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM prices WHERE product_id = %s', (product_id,))
            row = cur.fetchone()
            return jsonify(dict(row)) if row else ('', 404)

@app.route('/prices', methods=['POST'])
def create_price():
    time.sleep(1) # Calculate price using black magic
    data = request.json
    
    with get_db() as db:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('INSERT INTO prices (product_id, price) VALUES (%s, %s) RETURNING *', 
                       (data['product_id'], data['price']))
            row = cur.fetchone()
    
    # Publish to Kafka
    event = {
        'id': row['id'],
        'product_id': row['product_id'], 
        'price': float(row['price']), 
        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
        'action': 'created'
    }
    producer.produce(PRICE_TOPIC, key=str(row['product_id']), value=json.dumps(event))
    producer.flush()
    
    return jsonify(dict(row)), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRICE_SERVICE_PORT)