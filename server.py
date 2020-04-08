#!/usr/bin/env python

# python base modules
from threading import Lock
from queue import Queue, Empty

# dependencies
from flask import Flask, render_template, copy_current_request_context
from flask_socketio import SocketIO, emit

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)


class IMU(object):
    update_rate = 0.02  # [s]

    def __init__(self):
        self.thread = None
        self.thread_lock = Lock()  # ensure run() is running only one time
        self.latency_lock = Lock()  # ensure only one latency test at a time
        self.read_queue_lock = Lock()  # ensure only one task is reading values at a time (competing latency tests and run())
        self.count = 0
        self.data_queue = Queue(maxsize=0)  # maxsize=0 is infinite size queue

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
        with self.thread_lock:  # only one imu running at a time
            if self.thread is None:
                self.thread = socketio.start_background_task(self.run)

    def run(self):
        while True:
            socketio.sleep(self.update_rate)
            locked = self.read_queue_lock.acquire(False)
            if locked:
                if not self.data_queue.empty():
                    print('Latest data', self.get_last_data())  # will wait until data is in
                self.read_queue_lock.release()
            else:
                print('Run is paused during latency test')

    def measure_latency(self, n=50):
        data_list = []
        try:
            print('Start latency measuring')
            while True:
                locked =  self.read_queue_lock.acquire(False)  # block the run method, otherwise they both compete for data
                if locked:  
                    self.data_queue.queue.clear()
                    for i in range(n):
                        data = self.data_queue.get(timeout=1)  # can raise Empty
                        print('data', i, data)
                        if not data_list or data_list[-1][1:] != data[1:]:
                            # list was empty or exclude cases where the same data is twice in the list
                            data_list.append(data)
                    self.read_queue_lock.release()
                    deltas = [data2[0] - data1[0] for data2, data1 in zip(data_list[1:], data_list[:-1])]
                    latency = sum(deltas) / n
                    return latency
                else:
                    print('You should not see this message more than once')
        except Empty:
            # signal an error
            return -1

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
    #emit('server_response', {'text': 'Got {}'.format(message['data'])})


@socketio.on('latency_request')
def latency_request():
    latency_request_locked = imu.latency_lock.acquire(False)
    if latency_request_locked:
        # only start one latency task at a time
        @copy_current_request_context  # you need this decorator, otherwise emit does not know who to send the message to
        def send_latency():
            latency = imu.measure_latency()
            emit('latency', {'latency': latency})
            imu.latency_lock.release()
        socketio.start_background_task(send_latency)
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
    imu.start()
    emit('server_response', {'text': 'Client is connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0', debug=True)
