import time
import serial

from src.templates.thread_with_stop import ThreadWithStop
from src.utils.pipes import (laneDetectionToSerialError)


class threadSerial(ThreadWithStop):
    def __init__(self, pipes, debug=False):
        super(threadSerial, self).__init__()
        self._pipes = pipes
        self._debug = debug

        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)

        print("Connected to Arduino on /dev/ttyACM0 at 115200 baud.")
        
    def run(self):
        while self._running:

            # if self.ser.in_waiting > 0:
            #     line = self.ser.readline().decode('utf-8', errors='replace').strip()
            #     if line:
            #         print(f"[Arduino] {line}")
                    
            data = self._pipes.receive(laneDetectionToSerialError)

            if data is not None:
                data = data["bottom"]
                out_str = f"{data}\n"
                self.ser.write(out_str.encode('utf-8'))
                print(f"Sent angle={data} to Arduino.")

            time.sleep(0.01)

    def start(self):
        super(threadSerial, self).start()
    
    def stop(self):
        self.ser.close()
        print("Serial port closed.")
        super(threadSerial, self).stop()
