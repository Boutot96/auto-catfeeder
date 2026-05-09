import cv2
import requests
import serial

ser = serial.Serial('/dev/ttyUSB0', 9600)
SERVER = "http://192.168.0.203:5000"
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

frame_count = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame")
        continue

    if frame_count % 5 == 0:
        _, buffer = cv2.imencode('.jpg', frame)
        try:
            requests.post(f"{SERVER}/frame", data=buffer.tobytes(),
                headers={'Content-Type': 'application/octet-stream'})
            response = requests.get(f"{SERVER}/command")
            command = response.json()
            if command.get('dispense'):
                print("Dispensing food!")
                ser.write(b'D')
        except Exception as e:
            print(f"Error: {e}")

    frame_count += 1