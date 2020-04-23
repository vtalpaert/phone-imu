# python base modules
import threading
from queue import Queue, Empty
import time

# local files
from threads import BackgroundThread


class IMU(object):
    update_delay = 0.02  # [s]

    def __init__(self):
        self.data_queue = Queue(maxsize=0)  # maxsize=0 is infinite size queue
        self.is_recording = True  # start recording by default
        self.start()  # start the thread immediately

    def start(self):
        self.background_task = BackgroundThread(self, self.update_delay)
        self.clear_queue()
        self.background_task.start()

    def close(self):
        print('Closing background thread...')
        self.background_task.exit_event.set()
        time.sleep(0.1)

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
        if data[1:] != [0, 0, 0, 0, 0, 0] and self.is_recording:  # use a slice to ingore the timestamp
            # pass empty data
            self.data_queue.put(data)

    def run(self):
        """This method is executed in a loop by the background thread
        """
        if not self.data_queue.empty():
            data = self.get_first_data()
            print('Data', data)

    def action(self):
        self.is_recording = not self.is_recording
        return self.is_recording
