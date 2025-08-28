from flask import Flask, request, jsonify
import sqlite3
import json
from confluent_kafka import Producer
from config import PRODUCT_SERVICE_PORT, KAFKA_BOOTSTRAP_SERVERS, PRODUCT_TOPIC

app = Flask(__name__)
app.config['DATABASE'] = 'products.db'

producer = Producer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'partitioner': 'murmur2_random'
    })

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            description TEXT, 
            internal_sku TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        products = [
            ('Laptop', 'Gaming laptop', 'INT-LAP-001'),
            ('Mouse', 'Wireless mouse', 'INT-MOU-002'), 
            ('Keyboard', 'Mechanical keyboard', 'INT-KEY-003')
        ]
        for p in products:
            db.execute('INSERT OR IGNORE INTO products (name, description, internal_sku) VALUES (?, ?, ?)', p)
        
        # Publish initial products to Kafka (get timestamps from DB)
        for row in db.execute('SELECT * FROM products'):
            event = {
                'id': row['id'], 
                'name': row['name'], 
                'description': row['description'], 
                'internal_sku': row['internal_sku'], 
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'action': 'created'
            }
            producer.produce(PRODUCT_TOPIC, json.dumps(event))
        producer.flush()

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
        id = db.execute('''INSERT INTO products (name, description, internal_sku) 
                          VALUES (?, ?, ?)''', 
                       (data['name'], data.get('description', ''), data.get('internal_sku', ''))).lastrowid
        
        # Get the inserted row with timestamps
        row = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    
    # Publish to Kafka
    event = {
        'id': row['id'], 
        'name': row['name'], 
        'description': row['description'], 
        'internal_sku': row['internal_sku'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
        'action': 'created'
    }
    producer.produce(PRODUCT_TOPIC, key=str(id), value=json.dumps(event))
    producer.flush()
    
    return jsonify({'id': id, **data}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=PRODUCT_SERVICE_PORT)