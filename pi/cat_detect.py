import requests
import time
import random
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
cam = Picamera2()
cam.start()


SERVER = "http://192.168.0.203:5000"

cats = ["Lily", "Artemis", "unknown"]
event_types = ["detection", "dispense"]

frame_count = 0
while True:
    frame = cam.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
    if frame_count % 5 == 0:  # only run inference every 5 frames
        results = model(frame)
        results = model(frame)
        for box in results[0].boxes:
            print(box.cls)      # class index (e.g. 15 for cat in COCO)
            print(box.conf)     # confidence score
            print(box.xyxy)     # bounding box coordinates
            label = model.names[int(box.cls[0])]
            print(label)        # human readable label e.g. "cat"
        annotated = results[0].plot()
        cv2.imshow("Cat Detector", annotated)
    frame_count += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
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
    
cam.stop()
cv2.destroyAllWindows()