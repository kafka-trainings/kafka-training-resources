#!/usr/bin/env python3
from confluent_kafka import Producer
import json
import time
import random

# Function to generate random order data
def create_random_order_data():
    product_catalog = {'Apple': 0.30, 'Banana': 0.50, 'Chicken': 5.00, 'Milk': 1.20, 'Bread': 2.50, 'Eggs': 3.00}
    products = random.sample(list(product_catalog.items()), random.randint(1, 5))
    ordered_products = [product for product, _ in products]
    total_amount = sum(price for _, price in products)
    payment_methods = ['cash', 'card']
    payment_method = random.choice(payment_methods)
    order = {
        'ordered_products': ordered_products,
        'total_amount': round(total_amount, 2),
        'payment_method': payment_method,
        'order_timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return order

# Create a new Kafka Producer
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Continuously send messages
try:
    while True:
        # Generate a random message
        message = create_random_order_data()
        message_json = json.dumps(message)

        # Send the message to Kafka
        producer.produce('supermarket_purchases', value=message_json)
        print("Produced message: " + message_json)

        # Wait for one second before sending the next message
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    producer.flush()
