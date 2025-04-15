from flask import Flask, jsonify, request, send_from_directory
from Adafruit_IO import Client, Data
import dotenv

LED_FEED_NAME = "iot"
DOOR_FEED_NAME = "door"
FAN_FEED_NAME = "fan"

env_path = dotenv.find_dotenv(".env")  # Load the .env file
# Replace with your Adafruit IO credentials
ADAFRUIT_IO_KEY = dotenv.get_key(
    env_path, "ADAFRUIT_IO_KEY"
)  # Load from .env file or set directly
ADAFRUIT_IO_USERNAME = dotenv.get_key(
    env_path, "ADAFRUIT_IO_USERNAME"
)  # Load from .env file or set directly

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

app = Flask(__name__, static_folder="../web", static_url_path="/")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/api/fan/status", methods=["GET"])
def get_fan():
    try:
        fanstate = aio.receive(FAN_FEED_NAME)  # Replace with your feed name
        print(f"fan value: {fanstate.value}")    # Print the value attribute
        return jsonify({"value": fanstate.value})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/door/status", methods=["GET"])
def get_door():
    try:
        doorstate = aio.receive(DOOR_FEED_NAME)  # Replace with your feed name
        print(f"door value: {doorstate.value}")    # Print the value attribute
        return jsonify({"value": doorstate.value})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/light/status", methods=["GET"])
def get_led_status():
    print("Fetching LED status...")
    try:
        led_data = aio.receive(LED_FEED_NAME)  # Replace with your feed name
        print(f"LED status object: {led_data}")  # Print the entire object for debugging
        print(f"LED value: {led_data.value}")    # Print the value attribute
        return jsonify({"value": led_data.value})
    except Exception as e:
        print("error: ", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/api/fan/toggle", methods=["POST"])
def toggle_fan():
    try:
        current_state = aio.receive(FAN_FEED_NAME)  # Replace with your feed name
        new_state = "OFF" if current_state.value == "ON" else "ON"
        aio.send(FAN_FEED_NAME, new_state)
        return jsonify({"status": "success", "new_state": new_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/door/toggle", methods=["POST"])
def toggle_door():
    try:
        current_state = aio.receive(DOOR_FEED_NAME)  # Replace with your feed name
        new_state = "OFF" if current_state.value == "ON" else "ON"
        aio.send(DOOR_FEED_NAME, new_state)
        return jsonify({"status": "success", "new_state": new_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/light/toggle", methods=["POST"])
def toggle_led():
    try:
        current_state = aio.receive(LED_FEED_NAME)  # Replace with your feed name
        new_state = "OFF" if current_state.value == "ON" else "ON"
        aio.send(LED_FEED_NAME, new_state)
        return jsonify({"status": "success", "new_state": new_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Example of sending data to a feed (can be triggered by a POST request from the FE)
@app.route("/api/send/sensor_value", methods=["POST"])
def send_sensor_value():
    try:
        data = request.get_json()
        value = data.get("value")
        if value is not None:
            aio.send("sensor-data-feed", value)  # Replace with your feed name
            return jsonify({"status": "success", "sent_value": value}), 201
        else:
            return jsonify({"error": 'Missing "value" in request'}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)
