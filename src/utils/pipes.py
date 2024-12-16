from enum import Enum


class captureToPreprocess(Enum):
    transmitter = "processCapture"
    receiver = "processPreprocess"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

class preprocessToLaneDetection(Enum):
    transmitter = "processPreprocess"
    receiver = "processLaneDetection"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

class laneDetectionToDisplay(Enum):
    transmitter = "processLaneDetection"
    receiver = "processDisplay"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"
    
    