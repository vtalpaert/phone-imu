# python base modules
import threading
from queue import Queue, Empty
import time

# local files
from threads import BackgroundThread


class IMU(object):
    update_delay = 0.02  # [s]

    def __init__(self):
        self.latency_lock = threading.Lock()  # ensure only one latency test at a time
        self.queue_lock = threading.Lock()  # ensure only one task is reading values at a time (competing latency tests and run())
        self.count = 0  # counter for action_request
        self.data_queue = Queue(maxsize=0)  # maxsize=0 is infinite size queue
        self._exit_event = threading.Event()
        self.start()  # start the thread immediately

    def start(self):
        self.background_task = BackgroundThread(self, self.update_delay, self._exit_event, self.queue_lock)
        self.background_task.start()

    def close(self):
        print('Closing background thread...')
        self._exit_event.set()
        time.sleep(0.1)

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
        if data[1:] != [0, 0, 0, 0, 0, 0]:  # use a slice to ingore the timestamp
            # pass empty data
            self.data_queue.put(data)

    def run(self):
        """This method is executed in a loop by the background thread
        """
        if not self.data_queue.empty():
            data = self.get_last_data()  # will wait until data is in
            print('Latest data', data)
            # TODO do something with data, examples:
            # 1. calculate mean over last 100 values (use get_first_data in this case)
            # 2. calculate mean and std of time difference between two samples (with get_first_data)

    def measure_latency(self, n=50):
        data_list = []
        try:
            print('Start latency measuring')
            while True:
                locked =  self.queue_lock.acquire(False)  # block the run method, otherwise they both compete for data
                if locked:  
                    self.data_queue.queue.clear()
                    for i in range(n):
                        data = self.data_queue.get(timeout=1)  # can raise Empty
                        print('data', i, data)
                        if not data_list or data_list[-1][1:] != data[1:]:
                            # list was empty or exclude cases where the same data is twice in the list
                            data_list.append(data)
                    self.queue_lock.release()
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
