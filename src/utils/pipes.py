from enum import Enum


class captureToPreprocess(Enum):
    transmitter = "processCapture"
    receiver = "processPreprocess"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"

class preprocessToDisplay(Enum):
    transmitter = "processPreprocess"
    receiver = "processDisplay"
    enum_id = 1
    name = transmitter + "_" + receiver + "-" + str(enum_id)
    delivery_mode = "last"
    