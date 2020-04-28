# python base modules
import threading
from queue import Queue, Empty

# dependencies
from gevent import monkey, sleep
monkey.patch_all()  # fix gevent "this operation would block forever" depending on async_mode from server.py
# use sleep from gevent instead of time.sleep

# local files
#from threads import BackgroundThread
import draw


class IMU(object):
    thread_update_delay = 0.001  # [s]
    client_send_interval = 20  # [ms]
    live_plot = None  # holder

    def __init__(self):
        self.data_queue = Queue(maxsize=0)  # maxsize=0 is infinite size queue
        self.is_recording = True  # start recording by default
        self.steps = 0  # step counter
        self.live_plot = draw.LivePlot(n_values=3, title='Acceleration in (x, y, z)', ylabel='Value in [m/s²]')

    def close(self):
        if self.live_plot is not None:
            self.live_plot.close()

    def clear_queue(self):
        while not self.data_queue.empty():
            self.data_queue.get()

    def get_last_data(self):
        """Will clear the queue and keep only last element"""
        data = self.data_queue.get()  # waiting here until some data is in
        while not self.data_queue.empty():
            # update data with the latest value
            data = self.data_queue.get()  # consume queue
        return data

    def get_first_data(self):
        return self.data_queue.get()

    def get_first_data_or_none(self):
        try:
            return self.data_queue.get_nowait()
        except Empty:
            return None

    def add_data(self, data):
        if data[1:] != [0, 0, 0, 0, 0, 0] and self.is_recording:  # use a slice to ingore the timestamp
            # pass empty data
            self.data_queue.put(data)

    def run(self):
        """This method is executed in a loop by the background thread
        """
        data = self.get_first_data_or_none()
        if data is not None:
            self.live_plot.update(data[1:4])
            self.live_plot.draw()
        self.steps += 1

    def action(self):
        self.is_recording = not self.is_recording  # invert value
        return self.is_recording  # return current value

    def set_interval(self, interval):
        # this method is replaced when the client is connected (see server.py on('connect'))
        # we do this because we don't know who the client is when this file is compiled
        raise NotImplementedError('This method can only be called if a server is running')
