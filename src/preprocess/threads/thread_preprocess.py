import time
import cv2
import numpy as np

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import (preprocessToLaneDetectionImage, 
                            preprocessToLaneDetectionWarpPerspectiveMatrix,
                            captureToPreprocessImage,
                            captureToPreprocessImageDimensions)


class threadPreprocess(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(threadPreprocess, self).__init__()
        self._pipes = pipes
        self._debug = debug

        image_width, image_height = self._pipes.receive_wait(captureToPreprocessImageDimensions)

        offset = 50
        roi = {
            "src": np.float32([(round(0.312 * image_width) - offset, round(0.234 * image_width)), 
                               (round(0.687 * image_width) + offset, round(0.234 * image_width)),
                               (-round(0.14 * image_width) - offset, round(0.916 * image_height)),
                               (round(1.14 * image_width) + offset, round(0.916 * image_height))]),

            "dst": np.float32([(1, 1), (image_width, 1), (1, image_height), (image_width, image_height)])
        }
        
        self.warp_perspective = WarpPerspective(roi, image_width, image_height)
        self._pipes.transmit(preprocessToLaneDetectionWarpPerspectiveMatrix, [self.warp_perspective.])
        
    def run(self):
        while self._running:
            image = self._pipes.receive(captureToPreprocessImage)

            if image is None:
                time.sleep(0.001)
                continue

            preprocessed_image = ImagePreprocess().preprocess(image)
            warpPerspective_image = self.warp_perspective.transform(preprocessed_image)
        
            self._pipes.transmit(preprocessToLaneDetectionImage, warpPerspective_image)

    def start(self):
        super(threadPreprocess, self).start()
    
    def stop(self):
        super(threadPreprocess, self).stop()


class ImagePreprocess:
    @staticmethod    
    def preprocess(image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        sobel = cv2.Sobel(blurred_image, cv2.CV_8U, 1, 1, ksize=3)
        _, sobel_thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return sobel_thresh
    

class WarpPerspective:
    def __init__(self, roi, width, height):
        self.roi = roi
        self.image_shape = (width, height)
        self.transform_matrix, self.inverse_transform_matrix = self.calculate_transform_matrices()

    def calculate_transform_matrices(self):
        src, dst = self.roi["src"], self.roi["dst"]
        transform_matrix = cv2.getPerspectiveTransform(src, dst)
        inverse_transform_matrix = cv2.getPerspectiveTransform(dst, src)

        return transform_matrix, inverse_transform_matrix

    def transform(self, image):
        return cv2.warpPerspective(image, self.transform_matrix, self.image_shape)

    def inverseTransform(self, image):
        return cv2.warpPerspective(image, self.inverse_transform_matrix, self.image_shape)
    