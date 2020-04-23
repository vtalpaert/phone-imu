import threading
import weakref
import time


class BackgroundThread(threading.Thread):
    """
    Thread that executes parent.run() in a loop
    :param delay: pause between execution
    :param parent: will call run on parent
    """

    def __init__(self, parent, delay):
        threading.Thread.__init__(self)
        self.deamon = True
        self.delay = delay
        self.parent = weakref.proxy(parent)
        self.exit_event = threading.Event()

    def run(self):
        while not self.exit_event.is_set():
            self.parent.run()
            time.sleep(self.delay)
        print('Thread Exited')
