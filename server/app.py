from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

events = []

@app.route('/')
def dashboard():
    return render_template('dashboard.html', events=events)

@app.route('/detection', methods=['POST'])
def detection():
    data = request.json
    data['timestamp'] = datetime.now().strftime('%H:%M:%S')
    events.append(data)
    print(f"Detection: {data}")
    return jsonify({'status': 'ok'})

@app.route('/dispense', methods=['POST'])
def dispense():
    data = request.json
    data['timestamp'] = datetime.now().strftime('%H:%M:%S')
    events.append(data)
    print(f"Dispense: {data}")
    return jsonify({'status': 'ok'})

@app.route('/events', methods=['GET'])
def get_events():
    return jsonify(events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)