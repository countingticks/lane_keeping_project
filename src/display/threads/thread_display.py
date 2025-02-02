import cv2
import time
import numpy as np

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import (laneDetectionToDisplayImage, 
                            laneDetectionToDisplayData,
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
                lane_data = self._pipes.receive(laneDetectionToDisplayData)

                if lane_data is not None:

                    if self._debug:
                        print("left line:", lane_data["left"] is not None, "right lane", lane_data["right"] is not None)

                    if lane_data["left"] is not None:
                        cv2.polylines(real_image, [lane_data["left"]], False, (255, 0, 0), 2)

                    if lane_data["right"] is not None:
                        cv2.polylines(real_image, [lane_data["right"]], False, (0, 0, 255), 2)

                    if lane_data["middle"] is not None:
                        cv2.polylines(real_image, [lane_data["middle"]], False, (0, 255, 0), 2)

                cv2.imshow("real_image", real_image)
                cv2.waitKey(1)

            # display processed image
            image = self._pipes.receive(laneDetectionToDisplayImage)

            if self._debug:
                print("image: ", image)

            if image is not None:
                cv2.imshow("test", image)
                cv2.waitKey(1)

            time.sleep(0.01)

    def start(self):
        super(ThreadDisplay, self).start()
    
    def stop(self):
        super(ThreadDisplay, self).stop()
