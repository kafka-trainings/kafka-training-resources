import json
import time
import random
from datetime import datetime
from threading import Thread
from confluent_kafka  import Producer

# Path to the product catalog file
catalog_file_path = '/home/user/training/supermarket/product_catalog.txt'
producer_config_file_path = '/home/user/training/supermarket/config_producer.json'

# Load product names and prices from the file
def load_product_catalog(file_path):
    products = {}
    with open(file_path, 'r') as file:
        for line in file:
            name, price = line.strip().split(', ')
            products[name] = float(price)
    return products


# Global product catalog
product_catalog = load_product_catalog(catalog_file_path)

with open(producer_config_file_path, 'r') as f:
    producer_config = json.load(f)

# Kafka configuration
NUM_PRODUCERS = 5

# Possible values for order type and payment method
ORDER_TYPES = ['delivery', 'on_site']
PAYMENT_METHODS = ['cash', 'card']


def create_producer(config):
    # Create a new producer instance per thread
    producer = Producer(config)
    producer.init_transactions()
    return producer


def start_producers():
    threads = []
    for i in range(NUM_PRODUCERS):
        thread = Thread(target=produce_orders, args=(i,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def produce_orders(producer_id):
    producer = create_producer({
        'bootstrap.servers': producer_config['bootstrap_servers'],
        'enable.idempotence': producer_config['enable_idempotence'],
        'transactional.id': f"{producer_config['transactional_id']}-{producer_id}",
        'acks': producer_config['acks']
    })
    while True:
        try:
            producer.begin_transaction()
            order = create_order(producer_id)
            simulate_order_lifecycle(producer, order)
            producer.commit_transaction()
        except Exception as e:
            print(f"Error during order processing, aborting transaction: {e}")
            producer.abort_transaction()


# Function to create an order with random products
def create_order(producer_id):
    products = random.sample(list(product_catalog.items()), random.randint(1, 5))
    ordered_products = [product for product, _ in products]
    total_amount = sum(price for _, price in products)

    order_type = random.choices(ORDER_TYPES, weights=(1, 3), k=1)[0]
    order_status = 'completed' if order_type == 'on_site' else 'in preparation'
    payment_method = random.choice(PAYMENT_METHODS)

    order = {
        'order_id': f"{producer_id}-{int(time.time() * 1000)}",
        'supermarket_id': producer_id,
        'ordered_products': ordered_products,
        'order_timestamp': datetime.now().isoformat(),
        'order_status': order_status,
        'order_type': order_type,
        'total_amount': round(total_amount, 2),
        'payment_method': payment_method
    }
    return order


# Function to simulate the order lifecycle for delivery orders
def simulate_order_lifecycle(producer, order):
    try:

        # If the order is for delivery, we need to simulate the lifecycle
        if order['order_type'] == 'delivery':
            for status in ['in preparation', 'in delivery', 'completed']:
                order['order_status'] = status
                order['order_timestamp'] = datetime.now().isoformat()
                serialized_value = json.dumps(order).encode('utf-8')
                producer.produce(producer_config["topic"], value=serialized_value)
                print(f"Producer {order['supermarket_id']} produced {order}")
                if status != 'completed':
                    time.sleep(random.uniform(5,15))  # Random delay for next status
        else:
            # For on-site orders, send only the completed status
            serialized_value = json.dumps(order).encode('utf-8')
            producer.produce(producer_config["topic"], value=serialized_value)
            print(f"Producer {order['supermarket_id']} produced {order}")
        producer.flush()
    except Exception as e:
        print(f"Error during order lifecycle simulation: {e}")
        producer.abort_transaction()


# Start the producers
if __name__ == '__main__':
    start_producers()
