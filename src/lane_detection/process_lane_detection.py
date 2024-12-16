from src.templates.worker_process import WorkerProcess
from src.lane_detection.threads.thread_lane_detection import threadLaneDetection


class processLaneDetection(WorkerProcess):
    def __init__(self, pipes, debug=False):
        super(processLaneDetection, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def _init_threads(self):
        self.threads.append(threadLaneDetection(self._pipes, self._debug))

    def run(self):
        super(processLaneDetection, self).run()

    def stop(self):
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processLaneDetection, self).stop()
