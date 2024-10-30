import time
import cv2

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import preprocessToDisplay, captureToPreprocess


class threadPreprocess(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(threadPreprocess, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def run(self):
        while self._running:
            image = self._pipes.receive(captureToPreprocess)
            
            if image is None:
                time.sleep(0.001)
                continue
        
            self._pipes.transmit(preprocessToDisplay, image)
            time.sleep(0.001)

    def start(self):
        super(threadPreprocess, self).start()
    
    def stop(self):
        super(threadPreprocess, self).stop()
