import os
import subprocess
import webbrowser
import sys
import time
import signal

def main():
    try:
        # Define directories
        root_dir = os.getcwd()
        interface_dir = os.path.join(root_dir, "Interface")
        scripts_dir = os.path.join(interface_dir, "scripts")
        html_path = os.path.join(interface_dir, "index.html")

        # Step 1: Change to Interface directory
        print("Changing to Interface directory...")
        os.chdir(interface_dir)

        # Step 2: Start weather_api.py (runs server on port 5000)
        print("Starting weather_api.py server on port 5000...")
        weather_api_process = subprocess.Popen(
            [sys.executable, os.path.join(scripts_dir, "weather_api.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Step 3: Start simulation_api.py (runs server on port 5001)
        print("Starting simulation_api.py server on port 5001...")
        simulation_api_process = subprocess.Popen(
            [sys.executable, os.path.join(scripts_dir, "simulation_api.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Step 4: Give the API servers time to start
        time.sleep(2)

        # Step 5: Start local HTML server on port 3000
        print("Starting local server for index.html on port 3000...")
        html_server_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "3000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Step 6: Wait a moment and open index.html in the browser
        time.sleep(2)
        url = "http://localhost:3000/index.html"
        print(f"Opening {url} in browser...")
        webbrowser.open(url)

        print("Everything launched. Press Ctrl+C to shut down servers.")

        # Step 7: Keep the script alive until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down servers...")
        if 'weather_api_process' in locals():
            weather_api_process.send_signal(signal.SIGINT)
        if 'simulation_api_process' in locals():
            simulation_api_process.send_signal(signal.SIGINT)
        if 'html_server_process' in locals():
            html_server_process.terminate()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Cleaning up processes...")
        if 'weather_api_process' in locals() and weather_api_process.poll() is None:
            weather_api_process.terminate()
        if 'simulation_api_process' in locals() and simulation_api_process.poll() is None:
            simulation_api_process.terminate()
        if 'html_server_process' in locals() and html_server_process.poll() is None:
            html_server_process.terminate()

if __name__ == "__main__":
    main()