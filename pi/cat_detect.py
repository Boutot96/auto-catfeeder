import requests
import time
import random

SERVER = "http://192.168.0.203:5000"

cats = ["Lily", "Artemis", "unknown"]
event_types = ["detection", "dispense"]

while True:
    cat = random.choice(cats)
    event_type = random.choice(event_types)
    confidence = random.uniform(0.5, 0.99)
    weight = random.uniform(50, 200)

    payload = {
        'type': event_type,
        'cat': cat,
        'details': f"confidence: {confidence:.2f}, weight: {weight:.1f}g"
    }

    try:
        r = requests.post(f"{SERVER}/{event_type}", json=payload)
        print(f"Sent: {payload} -> {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2)