from enum import Enum


# CAPTURE TO PREPROCESS

class captureToPreprocessImage(Enum):
    transmitter = "processCapture"
    receiver = "processPreprocess"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

class captureToPreprocessImageDimensions(Enum):
    transmitter = "processCapture"
    receiver = "processPreprocess"
    enum_id = 2
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

# CAPTURE TO LANE DETECTION

class captureToLaneDetectionImageDimensions(Enum):
    transmitter = "processCapture"
    receiver = "processLaneDetection"
    enum_id = 3
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

# CAPTURE TO DISPLAY

class captureToDisplayImage(Enum):
    transmitter = "processCapture"
    receiver = "processDisplay"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

# PREPROCESS TO LANE DETECTION

class preprocessToLaneDetectionImage(Enum):
    transmitter = "processPreprocess"
    receiver = "processLaneDetection"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

class preprocessToLaneDetectionWarpPerspectiveMatrix(Enum):
    transmitter = "processPreprocess"
    receiver = "processLaneDetection"
    enum_id = 2
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

# LANE DETECTION TO DISPLAY

class laneDetectionToDisplayImage(Enum):
    transmitter = "processLaneDetection"
    receiver = "processDisplay"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"
    
class laneDetectionToDisplayData(Enum):
    transmitter = "processLaneDetection"
    receiver = "processDisplay"
    enum_id = 2
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"
    
# LANE DETECTION TO SERIAL

class laneDetectionToSerialError(Enum):
    transmitter = "processLaneDetection"
    receiver = "processSerial"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"
