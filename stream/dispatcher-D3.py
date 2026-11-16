import json
import os
import random
import time
from datetime import datetime, timezone
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "rapido-dispatch"

CITIES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "whitefield"],
}
TYPES = ["ride", "food"]


def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)

    seq = 0
    try:
        while True:
            seq += 1
            city = random.choice(list(CITIES.keys()))
            zone = random.choice(CITIES[city])
            order_type = random.choice(TYPES)
            routing_key = f"{city}.{zone}.{order_type}"

            payload = {
                "id": f"ORD-{seq:03d}",
                "city": city,
                "zone": zone,
                "type": order_type,
                "ts": datetime.now(timezone.utc).isoformat(),
            }

            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=json.dumps(payload),
            )
            print(f"[DISPATCHER] Sent #{seq} | key={routing_key} | msg={payload}", flush=True)
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()


if __name__ == "__main__":
    main()
