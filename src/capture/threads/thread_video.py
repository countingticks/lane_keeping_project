import time
import cv2

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import captureToPreprocess


class ThreadVideo(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(ThreadVideo, self).__init__()
        self._pipes = pipes
        self._debug = debug

        video_path = "src/assets/video.mp4"
        self._capture = cv2.VideoCapture(video_path)
        self._fps = 60

    def run(self):
        while self._running:
            ret, image = self._capture.read()
            
            if not ret:
                self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            self._pipes.transmit(captureToPreprocess, image)
            time.sleep(1 / self._fps)

    def start(self):
        super(ThreadVideo, self).start()
    
    def stop(self):
        super(ThreadVideo, self).stop()
