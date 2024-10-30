import time

from src.templates.thread_with_stop import ThreadWithStop


class ThreadCamera(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(ThreadCamera, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def run(self):
        while self._running:
            time.sleep(1)
            print("happy to be alive, live camera")

    def start(self):
        super(ThreadCamera, self).start()
    
    def stop(self):
        super(ThreadCamera, self).stop()
