import inspect

from enum import Enum
from multiprocessing import Pipe
from src.utils import pipes


class PipeStorage():
    def __init__(self, debug=False):
        self._pipes = {}
        self._debug = debug

        classes = inspect.getmembers(pipes, inspect.isclass) 
        for name, cls in classes:
            if name != "Enum" and issubclass(cls, Enum):
                self._create(cls.name.value, cls.delivery_mode.value)

    def _create(self, name, delivery_mode="default", duplex=False):
        recv, send = Pipe(duplex=duplex)
        self._pipes[name] = {"recv": recv, "send": send, "delivery_mode": delivery_mode}
        if self._debug:
            print("DEBUG: Pipe", name, "was successfully created!")

    def transmit(self, pipe, data):
        name = pipe.name.value
        self._pipes[name]["send"].send(data)

    def receive(self, pipe):
        name = pipe.name.value
        if not self._pipes[name]["recv"].poll():
            return None
        return self.receive_wait(pipe)

    def receive_wait(self, pipe):
        name = pipe.name.value
        data = self._pipes[name]["recv"].recv()
        delivery_mode =self._pipes[name]["delivery_mode"]

        if delivery_mode == "default": 
            return data

        if delivery_mode == "last":
            while (self._pipes[name]["recv"].poll()):
                data = self._pipes[name]["recv"].recv()
            return data

    def empty(self, pipe):
        name = pipe.name.value
        while (self._pipes[name].poll()):
            self._pipes[name]["recv"].recv()

    def is_data(self, pipe):
        name = pipe.name.value
        return self._pipes[name]["recv"].poll()
    
    def __del__(self):
        for name, pipe in self._pipes.items():
            pipe["recv"].close()
            pipe["send"].close()
            if self._debug:
                print("DEBUG: Pipe", name, "was successfully deleted!")
            