from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def send_data():
    while True:
        # Simulate data being sent from the server
        data = {"message": "Hello from the server!"}
        socketio.emit('update_data', data)
        time.sleep(5)  # Send data every 5 seconds

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Start the data sending thread when a client connects
    threading.Thread(target=send_data).start()

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
        
