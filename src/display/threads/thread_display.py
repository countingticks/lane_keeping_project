import cv2
import time
import numpy as np

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import (laneDetectionToDisplayImage, 
                            captureToDisplayImage)

class ThreadDisplay(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(ThreadDisplay, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def run(self):
        while self._running:
            # display real image
            real_image = self._pipes.receive(captureToDisplayImage)

            if self._debug:
                print("real image: ", real_image)

            if real_image is not None:
                cv2.imshow("real_image", real_image)
                cv2.waitKey(1)

            # display processed image
            image = self._pipes.receive(laneDetectionToDisplayImage)

            if self._debug:
                print("image: ", image)

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
