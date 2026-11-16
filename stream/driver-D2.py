import json
import os
import sys
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "rapido-dispatch"


def main():
    if len(sys.argv) < 3:
        print("Usage: python driver.py NAME PATTERN")
        sys.exit(1)

    driver_name = sys.argv[1]
    binding_pattern = sys.argv[2]

    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)

    # Declare a private exclusive queue and bind it with PATTERN
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=binding_pattern)

    print(f"[{driver_name}] Listening with pattern '{binding_pattern}' on queue '{queue_name}'...", flush=True)

    def on_message(ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))
        print(f"[{driver_name}] ACK | key={method.routing_key} | msg={data}", flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=False)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
