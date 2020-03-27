#!/usr/bin/env python
from threading import Lock
from queue import Queue
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)


class IMU(object):
    update_rate = 0.1  # [s]

    def __init__(self):
        self.thread = None
        self.thread_lock = Lock()
        self.count = 0
        self.data_queue = Queue(maxsize=0)  # infinite queue

    def get_last_data(self):
        """Will clear the queue and keep only last element"""
        data = self.data_queue.get()  # waiting here until some data is in
        while not self.data_queue.empty():
            data = self.data_queue.get()  # consume queue
        return data

    def get_first_data(self):
        """Will block until new data is here

        To ensure data is received quickly enough, you can try
        try:
            my_queue.get_nowait()
        except queue.Emtpy:
            pass  # do something if empty, for example reset
        but you will need to run this inside a timed/delayed loop
        """
        return self.data_queue.get()

    def add_data(self, data):
        if data[1:] != [0, 0, 0, 0, 0, 0]:  # use a slice to ingore the timestamp
            self.data_queue.put(data)

    def start(self):
        with self.thread_lock:
            if self.thread is None:
                self.thread = socketio.start_background_task(self.run)

    def run(self):
        while True:
            #socketio.sleep(self.update_rate)
            print('Latest data', self.get_last_data())  # will wait until data is in

    def action(self):
        self.count += 1
        return self.count

imu = IMU()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('incoming_data')
def test_message(message):
    imu.add_data(message['data'])
    emit('server_response', {'text': 'Got {}'.format(message['data'])})


@socketio.on('action_request')
def action_request():
    """Example of how to add an action on the IMU object"""
    count = imu.action()
    emit('server_response', {'text': 'Action was called {} times'.format(count)})


@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')


@socketio.on('connect')
def test_connect():
    print('Client connected')
    global imu
    imu.start()
    emit('server_response', {'text': 'Client is connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0', debug=True)
