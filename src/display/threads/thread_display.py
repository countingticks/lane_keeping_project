import cv2, time

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import preprocessToDisplay

class ThreadDisplay(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(ThreadDisplay, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def run(self):
        while self._running:            
            image = self._pipes.receive(preprocessToDisplay)

            if self._debug:
                print(image)

            if image is None:
                time.sleep(0.001)
                continue

            cv2.imshow("test", image)
            cv2.waitKey(1)
            time.sleep(0.001)

    def start(self):
        super(ThreadDisplay, self).start()
    
    def stop(self):
        super(ThreadDisplay, self).stop()
