from flask import Flask, jsonify, request
from Adafruit_IO import Client, Data

# Replace with your Adafruit IO credentials
ADAFRUIT_IO_KEY = 'YOUR_ADAFRUIT_IO_KEY'
ADAFRUIT_IO_USERNAME = 'YOUR_ADAFRUIT_IO_USERNAME'

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

app = Flask(__name__)

@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    try:
        temp_data = aio.receive('temperature-feed-name')  # Replace with your feed name
        return jsonify({'value': temp_data.value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/humidity', methods=['GET'])
def get_humidity():
    try:
        humidity_data = aio.receive('humidity-feed-name')  # Replace with your feed name
        return jsonify({'value': humidity_data.value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/led/status', methods=['GET'])
def get_led_status():
    try:
        led_data = aio.receive('led-control')  # Replace with your feed name
        return jsonify({'status': led_data.value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/led/toggle', methods=['POST'])
def toggle_led():
    try:
        current_state = aio.receive('led-control')  # Replace with your feed name
        new_state = 'OFF' if current_state.value == 'ON' else 'ON'
        aio.send('led-control', new_state)
        return jsonify({'status': 'success', 'new_state': new_state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example of sending data to a feed (can be triggered by a POST request from the FE)
@app.route('/api/send/sensor_value', methods=['POST'])
def send_sensor_value():
    try:
        data = request.get_json()
        value = data.get('value')
        if value is not None:
            aio.send('sensor-data-feed', value)  # Replace with your feed name
            return jsonify({'status': 'success', 'sent_value': value}), 201
        else:
            return jsonify({'error': 'Missing "value" in request'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)