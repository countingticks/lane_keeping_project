import cv2
import time
import numpy as np

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import laneDetectionToDisplay

class ThreadDisplay(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(ThreadDisplay, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def run(self):
        while self._running:            
            image = self._pipes.receive(laneDetectionToDisplay)

            if self._debug:
                print(image)

            if image is None:
                time.sleep(0.001)
                continue
            
            # image_width = 320
            # image_height = 240
            # offset = 0
            # roi = { "src": np.int32([(-round(0.14 * image_width) - offset, round(0.916 * image_height)), (round(1.14 * image_width) + offset, round(0.916 * image_height)), (round(0.75 * image_width) + offset, round(0.234 * image_width)), (round(0.25 * image_width) - offset, round(0.234 * image_width))])}

            # cv2.line(image, (roi["src"][0][0], roi["src"][0][1]), (roi["src"][1][0], roi["src"][1][1]), color=(255, 0, 0), thickness=2)
            # cv2.line(image, (roi["src"][1][0], roi["src"][1][1]), (roi["src"][2][0], roi["src"][2][1]), color=(255, 0, 0), thickness=2)
            # cv2.line(image, (roi["src"][2][0], roi["src"][2][1]), (roi["src"][3][0], roi["src"][3][1]), color=(255, 0, 0), thickness=2)
            # cv2.line(image, (roi["src"][3][0], roi["src"][3][1]), (roi["src"][0][0], roi["src"][0][1]), color=(255, 0, 0), thickness=2)

            cv2.imshow("test", image)
            cv2.waitKey(1)
            time.sleep(0.001)

    def start(self):
        super(ThreadDisplay, self).start()
    
    def stop(self):
        super(ThreadDisplay, self).stop()
