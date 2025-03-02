from src.templates.worker_process import WorkerProcess
from src.preprocess.threads.thread_preprocess import threadPreprocess


class processPreprocess(WorkerProcess):
    def __init__(self, pipes, debug=False):
        super(processPreprocess, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def _init_threads(self):
        self.threads.append(threadPreprocess(self._pipes, self._debug))

    def run(self):
        super(processPreprocess, self).run()

    def stop(self):
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processPreprocess, self).stop()
