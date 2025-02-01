import time
import picamera2

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import (captureToPreprocessImage, 
                            captureToDisplayImage, 
                            captureToPreprocessImageDimensions,
                            captureToLaneDetectionImageDimensions)


class ThreadCamera(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(ThreadCamera, self).__init__()
        self._pipes = pipes
        self._debug = debug

        self._fps = 30

        self._init_camera()
        self.send_image_size()

    def _init_camera(self):
        """This function will initialize the camera object. It will make this camera object have two chanels "lore" and "main"."""
        self.camera = picamera2.Picamera2()
        config = self.camera.create_preview_configuration(
            buffer_count=1,
            queue=False,
            main={"format": "XRGB8888", "size": (320, 240)}
        )
        self.camera.configure(config)
        self.camera.start()
        
    def run(self):
        while self._running:
            image = self.camera.capture_array("main")

            self._pipes.transmit(captureToPreprocessImage, image)
            self._pipes.transmit(captureToDisplayImage, image)

            time.sleep(1 / self._fps)

    def send_image_size(self):
        image = self.camera.capture_array("main")

        dimensions = [image.shape[1], image.shape[0]]

        self._pipes.transmit(captureToPreprocessImageDimensions, dimensions)
        self._pipes.transmit(captureToLaneDetectionImageDimensions, dimensions)

    def start(self):
        super(ThreadCamera, self).start()
    
    def stop(self):
        super(ThreadCamera, self).stop()
