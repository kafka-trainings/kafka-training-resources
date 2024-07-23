#!/usr/bin/env python3
import argparse
import signal
import sys
import time

from confluent_kafka import Producer


def print_table_header():
    print("┌──────┬──────────────┬───────┬────────────┬───────────┐")
    print("│ Part │ Offset       │ Key   │ Value      │ Timestamp │")
    print("├──────┼──────────────┼───────┼────────────┼───────────┤")


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    key_str = msg.key().decode("utf-8") if msg.key() else "None"
    value_str = msg.value().decode("utf-8") if msg.value() else "None"

    if err:
        print("Message delivery failed:")
        print(err)
        return

    # Print table header if it's the first message
    if not hasattr(delivery_report, "header_printed"):
        print_table_header()
        delivery_report.header_printed = True

    # Print table row
    partition_str = str(msg.partition()) if msg.partition() is not None else "?"
    offset_str = str(msg.offset()) if msg.offset() is not None else "?"
    timestamp_str = str(msg.timestamp()[1]) if msg.timestamp()[1] is not None else "?"
    print(f"│ {partition_str:^4} │ {offset_str:>12} │ {key_str:<5} │ {value_str:>10} │ {timestamp_str:>9} │")


producer = None


def main():
    global producer
    parser = argparse.ArgumentParser(description="Kafka Verifiable Producer")
    parser.add_argument("--topic", required=True, help="Produce messages to this topic.")
    parser.add_argument("--max-messages", type=int, default=-1,
                        help="Produce this many messages. If -1, produce messages until killed. (default: -1)")
    parser.add_argument("--throughput", type=int, default=1,
                        help="Throttle message throughput to THROUGHPUT messages/sec. (default: 1)")
    parser.add_argument("--acks", type=int, default=1, help="Acks required on each produced message. (default: 1)")
    parser.add_argument("--producer_config", help="Producer config properties file.")
    parser.add_argument("--value-prefix", help="Each produced value will have this prefix with a dot separator.")
    parser.add_argument("--repeating-keys", type=int,
                        help="Each produced record will have a key starting at 0 increment by 1 up to the number specified (exclusive), then reset to 0.")
    parser.add_argument("--bootstrap-server", required=True,
                        help="The server(s) to connect to. Comma-separated list of Kafka brokers in the form HOST1:PORT1,HOST2:PORT2,...")

    args = parser.parse_args()

    conf = {"bootstrap.servers": args.bootstrap_server,
            "partitioner": "murmur2_random",
            "acks": args.acks}

    if args.producer_config:
        with open(args.producer_config, "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                conf[key] = value

    producer = Producer(conf)

    key_counter = 0
    message_counter = 0
    start_time = time.time()
    try:
        while args.max_messages == -1 or message_counter < args.max_messages:
            if args.repeating_keys:
                key = str(key_counter).encode("utf-8")
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
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()
        sys.exit(0)

if __name__ == "__main__":
    main()
