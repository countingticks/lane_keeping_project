import time

from src.templates.thread_with_stop import ThreadWithStop
from src.lane_detection.lane_detect import LaneDetect
from src.utils.pipes import (preprocessToLaneDetectionImage, 
                            laneDetectionToDisplayImage,
                            captureToLaneDetectionImageDimensions)


class threadLaneDetection(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(threadLaneDetection, self).__init__()
        self._pipes = pipes
        self._debug = debug

        image_width, image_height = self._pipes.receive_wait(captureToLaneDetectionImageDimensions)

        self.lane_detect = LaneDetect(image_width, image_height)

    def run(self):
        while self._running:
            image = self._pipes.receive(preprocessToLaneDetectionImage)
            
            if image is None:
                time.sleep(0.001)
                continue

            lane_data = self.lane_detect.detect(image)

            if lane_data["lines"]["left"] is None and lane_data["lines"]["right"] is None:
                continue

            ReverseCoordinates().reverseLineCoordinates([lane_data["lines"]["left"], lane_data["lines"]["right"], lane_data["lines"]["middle"]], self.warpPerspective.inverseTransformMatrix)
        
            self._pipes.transmit(laneDetectionToDisplayImage, image)
            time.sleep(0.001)

    def start(self):
        super(threadLaneDetection, self).start()
    
    def stop(self):
        super(threadLaneDetection, self).stop()


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
