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


@socketio.on('latency_request')
def latency_request():
    latency_request_locked = imu.latency_lock.acquire(False)
    if latency_request_locked:
        # only start one latency task at a time
        @copy_current_request_context  # you need this decorator, otherwise emit does not know who to send the message back to
        def send_latency():
            print('start latency')
            latency = imu.measure_latency()
            # send to client the result
            emit('latency', {'latency': latency})
            # release lock unblocking new latency tests
            imu.latency_lock.release()
        # run function in background since it can take time
        socketio.start_background_task(send_latency)
        # emit acknowledgment before result is in
        emit('server_response', {'text': 'I started a latency test'})
    else:
        emit('server_response', {'text': 'The previous latency test is still running'})


@socketio.on('action_request')
def action_request():
    """Example of how to add an action on the IMU object"""
    print('Action called')
    count = imu.action()
    emit('server_response', {
        'text': 'Action was called {} times'.format(count),
        'count': count
    })


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
