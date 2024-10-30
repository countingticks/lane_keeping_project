from src.templates.worker_process import WorkerProcess
from src.capture.threads.thread_camera import ThreadCamera
from src.capture.threads.thread_video import ThreadVideo


class processCapture(WorkerProcess):
    def __init__(self, live_camera, pipes, debug=False):
        super(processCapture, self).__init__()
        self._live_camera = live_camera
        self._pipes = pipes
        self._debug = debug
        
    def _init_threads(self):
        if self._live_camera:
            self.threads.append(ThreadCamera(self._pipes, self._debug))
        else:
            self.threads.append(ThreadVideo(self._pipes, self._debug))

    def run(self):
        super(processCapture, self).run()

    def stop(self):
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processCapture, self).stop()
