from src.templates.worker_process import WorkerProcess
from src.serial.threads.thread_serial import threadSerial


class processSerial(WorkerProcess):
    def __init__(self, pipes, debug=False):
        super(processSerial, self).__init__()
        self._pipes = pipes
        self._debug = debug
        
    def _init_threads(self):
        self.threads.append(threadSerial(self._pipes, self._debug))

    def run(self):
        super(processSerial, self).run()

    def stop(self):
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processSerial, self).stop()
