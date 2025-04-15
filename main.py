import subprocess
import time
import webbrowser
import os

def run_flask_app():
    """Runs the Flask app in a separate process from the BE subdirectory."""
    try:
        app_path = os.path.join("BE", "app.py")
        process = subprocess.Popen(['python', app_path])
        print("Flask app started in the background.")
        return process
    except FileNotFoundError:
        print(f"Error: {app_path} not found. Make sure the directory structure is correct.")
        return None
    except Exception as e:
        print(f"Error starting Flask app: {e}")
        return None

def open_browser(url="http://127.0.0.1:5000/"):
    """Opens the default web browser to the specified URL."""
    try:
        webbrowser.open_new_tab(url)
        print(f"Opened browser to: {url}")
    except webbrowser.Error as e:
        print(f"Error opening browser: {e}")

if __name__ == "__main__":
    flask_process = run_flask_app()

    if flask_process:
        # Give the Flask app a little time to start up before opening the browser
        time.sleep(5)  # Adjust this value if needed

        open_browser()

        # Optionally, you can keep the main script running while the Flask app is active
        # You might want to add a way to gracefully stop the Flask app later.
        try:
            flask_process.wait()  # Wait for the Flask app process to finish
            print("Flask app finished.")
        except KeyboardInterrupt:
            print("Stopping Flask app...")
            flask_process.terminate()
            flask_process.wait()
            print("Flask app stopped.")