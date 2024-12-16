import time

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import preprocessToLaneDetection, laneDetectionToDisplay


class threadLaneDetection(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(threadLaneDetection, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def run(self):
        while self._running:
            image = self._pipes.receive(preprocessToLaneDetection)
            
            if image is None:
                time.sleep(0.001)
                continue
        
            self._pipes.transmit(laneDetectionToDisplay, image)
            time.sleep(0.001)

    def start(self):
        super(threadLaneDetection, self).start()
    
    def stop(self):
        super(threadLaneDetection, self).stop()
