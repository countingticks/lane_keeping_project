import time

from multiprocessing import Event
from src.utils.pipe_storage import PipeStorage
from src.capture.process_capture import processCapture
from src.preprocess.process_preprocess import processPreprocess
from src.lane_detection.process_lane_detection import processLaneDetection
from src.display.process_display import processDisplay
from src.serial.process_serial import processSerial


# flags
live_camera = True

# processes
processes = list()
blocker = Event()
pipes = PipeStorage(debug=True)

processes.append(processSerial(pipes, debug=False))
processes.append(processCapture(live_camera, pipes, debug=False))
processes.append(processPreprocess(pipes, debug=False))
processes.append(processLaneDetection(pipes, debug=False))
processes.append(processDisplay(pipes, debug=False))

print("\nStarting processes...\n") 
time.sleep(0.5)

for process in processes:
    process.daemon = True
    process.start()
    print(process)
print("\nAll processes started.\n")

try:
    blocker.wait()
    
except KeyboardInterrupt:
    print("\nStopping all processes...\n")
    time.sleep(0.5)

    for process in processes:
        process.stop()
        print(process)
print("\nAll processes stopped.\n")
