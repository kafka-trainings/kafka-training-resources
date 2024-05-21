import argparse
import json
import time
from confluent_kafka import Producer


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err:
        status = "error"
    else:
        status = "success"
    report = {
        "timestamp": int(time.time() * 1000),
        "topic": msg.topic(),
        "partition": msg.partition(),
        "offset": msg.offset(),
        "key": msg.key().decode('utf-8') if msg.key() else None,
        "value": msg.value().decode('utf-8'),
        "status": status
    }
    print(json.dumps(report))

def main():
    parser = argparse.ArgumentParser(description='Kafka Verifiable Producer')
    parser.add_argument('--topic', required=True, help='Produce messages to this topic.')
    parser.add_argument('--max-messages', type=int, default=-1,
                        help='Produce this many messages. If -1, produce messages until killed. (default: -1)')
    parser.add_argument('--throughput', type=int, default=1,
                        help='Throttle message throughput to THROUGHPUT messages/sec. (default: 1)')
    parser.add_argument('--acks', type=int, default=1, help='Acks required on each produced message. (default: 1)')
    parser.add_argument('--producer_config', help='Producer config properties file.')
    parser.add_argument('--message-create-time', type=int, default=-1,
                        help='Send messages with creation time starting at this value (milliseconds since epoch). (default: -1)')
    parser.add_argument('--value-prefix', help='Each produced value will have this prefix with a dot separator.')
    parser.add_argument('--repeating-keys', type=int,
                        help='Each produced record will have a key starting at 0 increment by 1 up to the number specified (exclusive), then reset to 0.')
    parser.add_argument('--bootstrap-server', required=True,
                        help='The server(s) to connect to. Comma-separated list of Kafka brokers in the form HOST1:PORT1,HOST2:PORT2,...')

    args = parser.parse_args()

    conf = {'bootstrap.servers': args.bootstrap_server,
            "partitioner": "murmur2_random"}

    if args.producer_config:
        with open(args.producer_config, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                conf[key] = value

    producer = Producer(conf)

    key_counter = 0
    message_counter = 0
    start_time = time.time()

    while args.max_messages == -1 or message_counter < args.max_messages:
        if args.repeating_keys:
            key = str(key_counter).encode('utf-8')
            key_counter = (key_counter + 1) % args.repeating_keys
        else:
            key = None

        value = f"{args.value_prefix}.{message_counter}" if args.value_prefix else str(message_counter)
        producer.produce(args.topic, key=key, value=value, callback=delivery_report)
        producer.poll(0)

        message_counter += 1

        if args.throughput > 0:
            elapsed_time = time.time() - start_time
            expected_time = message_counter / args.throughput
            if elapsed_time < expected_time:
                time.sleep(expected_time - elapsed_time)

    producer.flush()


if __name__ == "__main__":
    main()
