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
def incoming_data(message):
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
def connect():
    print('Client connected')
    #imu.start()
    emit('server_response', {'text': 'Client is connected'})
    @copy_current_request_context
    def set_interval(interval):
        # this method has an identified client to emit set_interval towards thanks to copy_current_request_context
        print('set interval to', interval)
        emit('set_interval', {'interval': interval})
    imu.set_interval = set_interval
    imu.set_interval(imu.client_send_interval)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    try:
        socketio.run(app, host= '0.0.0.0', debug=True)
    finally:
        imu.close()  # always close IMU when script is done
