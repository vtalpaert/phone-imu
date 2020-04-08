import threading
import weakref
import time


class BackgroundThread(threading.Thread):
    """
    Thread that executes parent.run() in a loop
    :param delay: pause between execution
    :param parent: will call run on parent
    :param exit_event: (threading.Event object)
    :param lock: (threading.Lock)
    """

    def __init__(self, parent, delay, exit_event, lock):
        threading.Thread.__init__(self)
        self.deamon = True
        self.delay = delay
        self.parent = weakref.proxy(parent)
        self.exit_event = exit_event
        self.lock = lock

    def run(self):
        while not self.exit_event.is_set():
            with self.lock:
                self.parent.run()
            time.sleep(self.delay)
        print('Thread Exited')
