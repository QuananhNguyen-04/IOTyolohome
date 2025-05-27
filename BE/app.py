import sys
from flask import Flask, jsonify, request, send_from_directory
from Adafruit_IO import Client, Data
import dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone

LED_FEED_NAME = "iot"
DOOR_FEED_NAME = "door"
FAN_FEED_NAME = "fan"
TEMPERATURE_FEED_NAME = "temp"
LIGHT = "light"
HUMID = "humid"

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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard_data.db'  # Use SQLite
db: SQLAlchemy = SQLAlchemy(app)

# Define database models
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=7))))
    value = db.Column(db.Float)

class Humidity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=7))))
    value = db.Column(db.Float)

class LightIntensity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=7))))
    value = db.Column(db.Float)

class FanStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=7))))
    value = db.Column(db.String(50))

class DoorStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=7))))
    value = db.Column(db.String(50))

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/temperature", methods=["GET"])
def get_temperature():
    try:
        temp_data = aio.receive(TEMPERATURE_FEED_NAME) 
        value = float(temp_data.value)
        new_entry = Temperature(value=value)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"value": value})
    except Exception as e:
        print(f"Error getting/saving temperature: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/humidity", methods=["GET"])
def get_humidity():
    try:
        humidity_data = aio.receive(HUMID)
        value = float(humidity_data.value)
        new_entry = Humidity(value=value)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"value": value})
    except Exception as e:
        print(f"Error getting/saving humidity: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/light", methods=["GET"])
def get_light_intensity():
    try:
        light_data = aio.receive(LIGHT)
        value = float(light_data.value)
        new_entry = LightIntensity(value=value)
        print("new_entry")
        db.session.add(new_entry)
        db.session.commit()
        print("data added")
        return jsonify({"value": value})
    except Exception as e:
        print(f"Error getting/saving light intensity: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/fan/status", methods=["GET"])
def get_fan():
    try:
        fanstate = aio.receive(FAN_FEED_NAME)  # Replace with your feed name
        print(f"fan value: {fanstate.value}")  # Print the value attribute
        value = fanstate.value
        new_entry = FanStatus(value=value)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"value": fanstate.value})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/door/status", methods=["GET"])
def get_door():
    try:
        doorstate = aio.receive(DOOR_FEED_NAME)  # Replace with your feed name
        print(f"door value: {doorstate.value}")  # Print the value attribute
        value = doorstate.value
        new_entry = DoorStatus(value=value)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"value": doorstate.value})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/light/status", methods=["GET"])
def get_led_status():
    print("Fetching LED status...")
    try:
        led_data = aio.receive(LED_FEED_NAME)  # Replace with your feed name
        print(f"LED status object: {led_data}")  # Print the entire object for debugging
        print(f"LED value: {led_data.value}")  # Print the value attribute
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
        print("Fan toggled")
        return jsonify({"status": "success", "new_state": new_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/fan/speed", methods=["POST"])
def set_fan_speed():
    try:
        data = request.get_json()
        speed = int(data.get("speed", 0))

        if not (1 <= speed <= 100):
            return jsonify({"error": "Speed must be between 1 and 100"}), 400

        aio.send(FAN_FEED_NAME, speed)

        return jsonify({"status": "success", "new_speed": speed})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/door/toggle", methods=["POST"])
def toggle_door():
    try:
        current_state = aio.receive(DOOR_FEED_NAME)  # Replace with your feed name
        new_state = "OFF" if current_state.value == "ON" else "ON"
        aio.send(DOOR_FEED_NAME, new_state)
        print("Door toggled")
        return jsonify({"status": "success", "new_state": new_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/light/toggle", methods=["POST"])
def toggle_led():
    try:
        current_state = aio.receive(LED_FEED_NAME)  # Replace with your feed name
        new_state = "OFF" if current_state.value == "ON" else "ON"
        aio.send(LED_FEED_NAME, new_state)
        print("Light toggled")
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


# New API endpoints to get historical data
@app.route("/api/historical/temperature", methods=["GET"])
def get_historical_temperature():
    try:
        historical_data = Temperature.query.order_by(Temperature.timestamp).all()
        data_points = [{"timestamp": entry.timestamp.isoformat(), "value": entry.value} for entry in historical_data]
        return jsonify(data_points)
    except Exception as e:
        print(f"Error getting historical temperature data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/historical/humidity", methods=["GET"])
def get_historical_humidity():
    try:
        historical_data = Humidity.query.order_by(Humidity.timestamp).all()
        data_points = [{"timestamp": entry.timestamp.isoformat(), "value": entry.value} for entry in historical_data]
        return jsonify(data_points)
    except Exception as e:
        print(f"Error getting historical humidity data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/historical/light", methods=["GET"])
def get_historical_light():
    try:
        historical_data = LightIntensity.query.order_by(LightIntensity.timestamp).all()
        data_points = [{"timestamp": entry.timestamp.isoformat(), "value": entry.value} for entry in historical_data]
        return jsonify(data_points)
    except Exception as e:
        print(f"Error getting historical light intensity data: {e}")
        return jsonify({"error": str(e)}), 500


def main(argv):
    port = 5000  # Default port

    if "--port" in argv:
        try:
            port_index = argv.index("--port")
            if port_index + 1 < len(argv):
                port_value = argv[port_index + 1]
                port = int(port_value)
            else:
                print("Error: --port argument requires a port number.")
        except ValueError:
            print("Error: Invalid port number provided.")
        except IndexError:
            print("Error: --port argument requires a port number.")

    app.run(debug=True, port=port)

if __name__ == "__main__":
    main(sys.argv[1:])