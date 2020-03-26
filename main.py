#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)


class IMU(object):
    update_rate = 5  # [s]

    def __init__(self):
        self.thread = None
        self.thread_lock = Lock()
        self.count = 0

    def start(self):
        with self.thread_lock:
            if self.thread is None:
                self.thread = socketio.start_background_task(self.run)

    def run(self):
        while True:
            socketio.sleep(self.update_rate)
            socketio.emit('my_response',
                        {'data': 'Server generated event', 'count': self.count},
            )

    def action(self):
        self.count += 1

imu = IMU()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('action_request')
def action_request():
    imu.action()
    emit('my_response', {'data': 'Action was called', 'count': 0})


@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')


@socketio.on('connect')
def test_connect():
    global imu
    imu.start()
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True)
