from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import json
from confluent_kafka import Producer
from config import PRODUCT_SERVICE_PORT, KAFKA_BOOTSTRAP_SERVERS, PRODUCT_TOPIC

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'products_db',
    'user': 'user',
    'password': 'password'
}

producer = Producer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'partitioner': 'murmur2_random'
    })

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY, 
                name VARCHAR(255), 
                description TEXT, 
                internal_sku VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            products = [
                ('Laptop', 'Gaming laptop', 'INT-LAP-001'),
                ('Mouse', 'Wireless mouse', 'INT-MOU-002'), 
                ('Keyboard', 'Mechanical keyboard', 'INT-KEY-003')
            ]
            for p in products:
                cur.execute('''INSERT INTO products (name, description, internal_sku) 
                              VALUES (%s, %s, %s) ON CONFLICT DO NOTHING''', p)
            
            # Publish initial products to Kafka (get timestamps from DB)
            cur.execute('SELECT * FROM products')
            for row in cur.fetchall():
                event = {
                    'id': row[0], 
                    'name': row[1], 
                    'description': row[2], 
                    'internal_sku': row[3], 
                    'created_at': row[4].isoformat() if row[4] else None,
                    'updated_at': row[5].isoformat() if row[5] else None,
                    'action': 'created'
                }
                producer.produce(PRODUCT_TOPIC, key=str(row[0]), value=json.dumps(event))
            producer.flush()

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
            cur.execute('''INSERT INTO products (name, description, internal_sku) 
                          VALUES (%s, %s, %s) RETURNING *''', 
                       (data['name'], data.get('description', ''), data.get('internal_sku', '')))
            row = cur.fetchone()
    
    # Publish to Kafka
    event = {
        'id': row['id'], 
        'name': row['name'], 
        'description': row['description'], 
        'internal_sku': row['internal_sku'],
        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
        'action': 'created'
    }
    producer.produce(PRODUCT_TOPIC, key=str(row['id']), value=json.dumps(event))
    producer.flush()
    
    return jsonify({'id': row['id'], **data}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRODUCT_SERVICE_PORT)