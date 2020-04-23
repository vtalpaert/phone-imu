#!/usr/bin/env python

# dependencies
from flask import Flask, render_template, copy_current_request_context
from flask_socketio import SocketIO, emit

# local files
from imu import IMU


imu = IMU()  # unique instance of IMU

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('incoming_data')
def test_message(message):
    imu.add_data(message['data'])
    #emit('server_response', {'text': 'Got {}'.format(message['data'])})


@socketio.on('action_request')
def action_request():
    is_recording = imu.action()
    if is_recording:
        emit('server_response', {'text': 'IMU is now recording', 'recording': True})
    else:
        emit('server_response', {'text': 'IMU has stopped recording', 'recording': False})


@socketio.on('connect')
def test_connect():
    print('Client connected')
    #imu.start()
    emit('server_response', {'text': 'Client is connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    try:
        socketio.run(app, host= '0.0.0.0', debug=True)
    finally:
        imu.close()  # always close IMU when script is done
