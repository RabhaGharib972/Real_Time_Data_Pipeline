import requests
import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    try:
        response = requests.get("https://randomuser.me/api/")
        data = response.json()["results"][0]

        user = {
            "id": data["login"]["uuid"],
            "name": data["name"]["first"] + " " + data["name"]["last"],
            "gender": data["gender"],
            "email": data["email"],
            "country": data["location"]["country"]
        }

        print("Sending:", user)
        producer.send("randomuser-topic", value=user)
        producer.flush()

        time.sleep(3)

    except Exception as e:
        print("Producer Error:", e)
        time.sleep(5)
