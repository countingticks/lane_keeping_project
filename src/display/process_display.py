from src.templates.worker_process import WorkerProcess
from src.display.threads.thread_display import ThreadDisplay


class processDisplay(WorkerProcess):
    def __init__(self, pipes, debug=False):
        super(processDisplay, self).__init__()
        self._pipes = pipes
        self._debug = debug

    def _init_threads(self):
        self.threads.append(ThreadDisplay(self._pipes, self._debug))

    def run(self):
        super(processDisplay, self).run()

    def stop(self):
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processDisplay, self).stop()
