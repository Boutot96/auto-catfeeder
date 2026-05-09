from flask import Flask, request, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import cv2
import numpy as np
from ultralytics import YOLO
import time

model = YOLO("best_v2.pt")
latest_frame = None
pending_command = None
lunch_fed = False
dinner_fed = False

app = Flask(__name__)

events = []

MAX_FEEDS_PER_DAY = 3
MIN_TIME_BETWEEN_FEEDS = timedelta(hours=5)
feed_log = []

scheduler = BackgroundScheduler()


def scheduled_feed():
    global pending_command, lunch_fed, dinner_fed
    now = datetime.now()
    hour = now.hour
    
    if hour == 0 and not lunch_fed:
        lunch_fed = True
        _do_feed('scheduled lunch')
    elif hour == 19 and not dinner_fed:
        dinner_fed = True
        _do_feed('scheduled dinner')
    elif hour == 6:
        _do_feed('scheduled breakfast')
        lunch_fed = False  # reset for the day
        dinner_fed = False

def _do_feed(details):
    global pending_command
    pending_command = {'dispense': True, 'cat': 'lily'}
    events.append({
        'type': 'dispense',
        'cat': 'lily',
        'details': details,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })
    
# 6am every day
scheduler.add_job(scheduled_feed, 'cron', hour=6, minute=0)
# 1pm fallback
scheduler.add_job(scheduled_feed, 'cron', hour=13, minute=0)
# 8pm fallback
scheduler.add_job(scheduled_feed, 'cron', hour=19, minute=0)

scheduler.start()


def can_feed():
    global lunch_fed, dinner_fed
    now = datetime.now()
    today = now.date()
    feeds_today = [f for f in feed_log if f.date() == today]
    if len(feeds_today) >= MAX_FEEDS_PER_DAY:
        return False
    if feed_log and (now - feed_log[-1]) < MIN_TIME_BETWEEN_FEEDS:
        return False
    return True


def in_feeding_window():
    hour = datetime.now().hour
    return (11 <= hour < 13) or (16 <= hour < 19)


@app.route('/')
def dashboard():
    return render_template('dashboard.html', events=events)

@app.route('/manual_feed', methods=['POST'])
def manual_feed():
    global pending_command
    pending_command = {'dispense': True, 'cat': 'manual'}
    return jsonify({'status': 'ok'})

@app.route('/frame', methods=['POST'])
def receive_frame():
    global latest_frame, lunch_fed, dinner_fed, pending_command
    nparr = np.frombuffer(request.data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if not in_feeding_window():
        latest_frame = frame  # still update the feed
        return jsonify({'status': 'ok'})
    results = model(frame)
    latest_frame = results[0].plot()
    
    # check for cats
    for box in results[0].boxes:
        label = model.names[int(box.cls[0])]
        conf = box.conf[0].item()
        if label == 'lily' and conf > 0.5:
            # Record hour to determine feeding window
            hour = datetime.now().hour
            if can_feed():
                if 11 <= hour < 13:
                    lunch_fed = True
                elif 16 <= hour < 19:
                    dinner_fed = True
                feed_log.append(datetime.now())
                pending_command = {'dispense': True, 'cat': 'lily'}
                events.append({
                    'type': 'detection',
                    'cat': 'lily',
                    'details': f"confidence: {conf:.2f}",
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
    return jsonify({'status': 'ok'})


@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if latest_frame is not None:
                _, buffer = cv2.imencode('.jpg', latest_frame)
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.0333)
    return app.response_class(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/command')
def command():
    global pending_command
    cmd = pending_command
    pending_command = None
    if cmd is None:
        return jsonify({})
    return jsonify(cmd)


@app.route('/events')
def get_events():
    return jsonify(events)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)