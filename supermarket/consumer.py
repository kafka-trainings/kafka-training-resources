#!/usr/bin/env python3
from confluent_kafka import Consumer, Producer
import json

props = {'bootstrap.servers': 'localhost:9092',
         'group.id': 'hallo_dev_consumer',
         'enable.auto.commit': False,
         'auto.offset.reset': 'earliest'}
c = Consumer(props)

try:
    c.subscribe(['supermarket_purchases'])
    while True:
        message = c.poll(100)
        if message is None:
            continue
        if message.error():
            print("Consumer error: {}".format(message.error()))
            continue
        print("Received Order: {}".format(message.value().decode('utf-8')))
finally:
    c.close()