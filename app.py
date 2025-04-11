import os
import subprocess
import webbrowser
import sys

def main():
    try:
        # Step 1: Navigate to the 'Interface' directory
        print("Navigating to the 'Interface' directory...")
        os.chdir("Interface")

        # Step 2: Navigate to the 'scripts' subdirectory
        print("Navigating to the 'scripts' subdirectory...")
        os.chdir("scripts")

        # Step 3: Run the weather_api.py script
        print("Running weather_api.py...")
        result = subprocess.run([sys.executable, "weather_api.py"], check=True)
        if result.returncode == 0:
            print("weather_api.py executed successfully.")
        else:
            print("Error: weather_api.py did not execute successfully.")
            return

        # Step 4: Navigate back to the 'Interface' directory
        print("Navigating back to the 'Interface' directory...")
        os.chdir("..")

        # Step 5: Open index.html in the default web browser
        print("Launching index.html...")
        html_path = os.path.abspath("index.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file://{html_path}")
            print(f"Opened {html_path} in the default browser.")
        else:
            print(f"Error: {html_path} does not exist.")

    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()