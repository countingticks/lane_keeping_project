import time
import numpy as np

from src.templates.thread_with_stop import ThreadWithStop
from src.lane_detection.lane_detect import LaneDetect
from src.utils.pipes import (preprocessToLaneDetectionImage,
                            preprocessToLaneDetectionWarpPerspectiveMatrix,
                            laneDetectionToDisplayData,
                            laneDetectionToDisplayImage,
                            laneDetectionToSerialError,
                            captureToLaneDetectionImageDimensions)


class threadLaneDetection(ThreadWithStop):
    def __init__(self, serial, pipes, debug=False):
        super(threadLaneDetection, self).__init__()
        self._pipes = pipes
        self._debug = debug
        self._serial = serial

        self.image_width, image_height = self._pipes.receive_wait(captureToLaneDetectionImageDimensions)

        self.lane_detect = LaneDetect(self.image_width, image_height)
        self.warp_perspective_inverse_matrix = self._pipes.receive_wait(preprocessToLaneDetectionWarpPerspectiveMatrix)

    def run(self):
        while self._running:
            image = self._pipes.receive(preprocessToLaneDetectionImage)
            
            if image is None:
                time.sleep(0.01)
                continue

            lane_data = self.lane_detect.detect(image, self._debug)

            if lane_data["left"] is not None or lane_data["right"] is not None:
                if self._serial:
                    self._pipes.transmit(laneDetectionToSerialError, DistanceError.getError(lane_data, self.image_width))
                    
                ReverseCoordinates().reverseLineCoordinates([lane_data["left"], lane_data["right"], lane_data["middle"]], self.warp_perspective_inverse_matrix)

                self._pipes.transmit(laneDetectionToDisplayImage, image)
                self._pipes.transmit(laneDetectionToDisplayData, lane_data)
                
            time.sleep(0.01)

    def start(self):
        super(threadLaneDetection, self).start()
    
    def stop(self):
        super(threadLaneDetection, self).stop()



class DistanceError:
    @staticmethod
    def getError(lane_data, image_width):
        if lane_data["middle"] is not None:
            error_top = image_width / 2 - lane_data["middle"][0][0]
            error_middle = image_width / 2 - lane_data["middle"][len(lane_data["middle"]) // 2][0]
            error_bottom = image_width / 2 - lane_data["middle"][-1][0]

            # error_top = self.pixelsToCentimeters(error_top, lane_data, lane_data["lines"]["middle"][0][1])
            # error_bottom = self.pixelsToCentimeters(error_bottom, lane_data, lane_data["lines"]["middle"][-1][1])

            return { "top": error_top, "middle": error_middle, "bottom": error_bottom }
        
        return None
    


class ReverseCoordinates:
    @staticmethod
    def reverseLineCoordinates(lanes, inverseTransformMatrix):
        transformMatrix = inverseTransformMatrix

        for lane in lanes:
            if lane is None:
                continue

            coords = np.hstack((lane, np.ones((lane.shape[0], 1), dtype=np.float32)))

            transformedCoords = np.dot(coords, transformMatrix.T)
            transformedCoords /= transformedCoords[:, 2][:, np.newaxis]

            lane[:, 0] = transformedCoords[:, 0].astype(int)
            lane[:, 1] = transformedCoords[:, 1].astype(int)

    @staticmethod
    def reverseWindowsCoordinates(windows, inverseTransformMatrix):
        if windows is None:
            return
        
        transformMatrix = inverseTransformMatrix

        for window in windows:
            for pointPair in window:
                coords = np.hstack((pointPair, [1.0]))

                transformedCoords = np.dot(coords, transformMatrix.T)
                transformedCoords /= transformedCoords[2]

                pointPair[0] = int(transformedCoords[0])
                pointPair[1] = int(transformedCoords[1])
