from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

# Variable to track if the script is running
is_running = False
process = None

@app.route('/run-script', methods=['POST'])
def run_script():
    global is_running, process
    if is_running:
        return jsonify(status='error', message='Script is already running')

    try:
        # Start the Python script in a non-blocking way
        process = subprocess.Popen(['python', 'run_automated_platform.py'])
        is_running = True
        
        # Return a success message
        return jsonify(status='success', message='Number Plate Successfully detected')
    except Exception as e:
        return jsonify(status='error', message=str(e))

@app.route('/script-finished', methods=['POST'])
def script_finished():
    global is_running
    is_running = False
    return jsonify(status='success', message='Script has finished execution')

if __name__ == '__main__':
    app.run(port=5000)
