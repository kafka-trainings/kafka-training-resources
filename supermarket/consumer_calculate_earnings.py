from confluent_kafka import Consumer, KafkaError
import json
from time import time

# Configuration
catalog_file_path = '/home/user/training/supermarket/product_catalog.txt'
consumer_config_file_path = '/home/user/training/supermarket/config_consumer.json'

def load_product_catalog(file_path):
    products = {}
    with open(file_path, 'r') as file:
        for line in file:
            name, price = line.strip().split(', ')
            products[name] = float(price)
    return products


product_catalog = load_product_catalog(catalog_file_path)

with open(consumer_config_file_path, 'r') as f:
    consumer_config = json.load(f)

# Initialize an empty dictionary to store supplier costs
supplier_costs = {}
# Initialize an empty dictionary to store transaction earnings
transaction_earnings = {}
# Initialize a dictionary to store earnings per supermarket and a variable for total earnings
earnings_per_supermarket = {}
total_earnings = 0


consumer = Consumer({
    'bootstrap.servers': consumer_config["bootstrap_servers"],
    'group.id': consumer_config["group_id"],
    'enable.auto.commit': consumer_config["enable_auto_commit"],
    'auto.offset.reset': consumer_config["auto_offset_reset"],
    'isolation.level': consumer_config["isolation_level"]  # Only read committed messages
})

initial_topic = "sqlite_supplier_costs"
consumer.subscribe([initial_topic])


# Process only the initial topic
def consume_initial_topic():
    print("Consuming messages from the initial topic...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("No more messages in initial topic.")
                break
            if msg.error():
                print(f"Error: {msg.error()}")
                break
            data = json.loads(msg.value().decode('utf-8'))
            update_supplier_costs(data)
    finally:
        consumer.unsubscribe()
        print(f'Unsubscribed from init topic.')



def process_message(msg):
    if msg.topic() == "customer_transactions":
        transaction = json.loads(msg.value().decode('utf-8'))
        calculate_earnings(transaction)
        consumer.commit(message=msg)
    elif msg.topic() == "sqlite_supplier_costs":
        data = json.loads(msg.value().decode('utf-8'))
        update_supplier_costs(data)


# Function to update supplier costs dictionary with latest cost info
def update_supplier_costs(data):
    payload = data.get('payload', {})

    if payload:
        product_name = payload.get('product_name')
        supermarket_id = payload.get('supermarket_id')
        cost_per_item = payload.get('cost_per_item')

        # Check if all necessary data is present
        if product_name and supermarket_id is not None and cost_per_item is not None:
            key = (product_name, supermarket_id)
            supplier_costs[key] = cost_per_item
            print(f"Updated supplier_costs for {key}: {cost_per_item}")  # Debugging
        else:
            print("missing data in payload:", payload) #debugging


def calculate_earnings(transaction):
    global total_earnings
    earnings = 0
    supermarket_id = transaction['supermarket_id']
    print(f"Processing transaction {transaction['order_id']} for supermarket {supermarket_id}")

    for product in transaction['ordered_products']:
        key = (product, supermarket_id)
        supplier_cost = supplier_costs.get(key)
        selling_price = product_catalog.get(product)

        if supplier_cost is not None and selling_price is not None:
            product_earnings = selling_price - supplier_cost
            earnings += product_earnings
            print(f"Product: {product}, Earnings: {product_earnings}")
        else:
            print(f"Missing cost or selling price for product {product}")

    # Update the earnings per supermarket and the total earnings
    earnings_per_supermarket[supermarket_id] = earnings_per_supermarket.get(supermarket_id, 0) + earnings
    total_earnings += earnings
    print(f"Earnings for this transaction: {earnings}")
    print(f'Total earnings: {total_earnings}')


def consume_other_topics():
    other_topics = consumer_config["topics"]
    consumer.subscribe(other_topics)
    print(f"Subscribed to {other_topics} for further processing.")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue  # End of partition event
                elif msg.error().code() == KafkaError.NO_ERROR:
                    continue  # No error on polling
                else:
                    print(msg.error())
                    break
            process_message(msg)
    except KeyboardInterrupt:
        print('Interrupted by user')
    finally:
        # Clean up on close
        consumer.close()


# Run the consumption process
consume_initial_topic()
consume_other_topics()