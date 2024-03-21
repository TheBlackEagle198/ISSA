import struct


class InvalidMessageError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidMessageTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Message:
    MSG_REGISTER = 0
    MSG_POST_CAR = 1
    MSG_REQUEST_CARS = 2
    MSG_START_RENTAL = 3
    MSG_END_RENTAL = 4
    MSG_CAR_LIST = 5

    ERR_SUCCESS = 6
    ERR_BAD_FORMAT = 7
    ERR_INVALID_TYPE = 8
    ERR_ALREADY_REGISTERED = 9
    ERR_NOT_REGISTERED = 10
    ERR_ALREADY_RENTED = 11
    ERR_NOT_RENTED = 12
    ERR_CAR_UNAVAILABLE = 13

    type_to_str = {
        MSG_REGISTER: "MSG_REGISTER",
        MSG_POST_CAR: "MSG_POST_CAR",
        MSG_REQUEST_CARS: "MSG_REQUEST_CARS",
        MSG_START_RENTAL: "MSG_START_RENTAL",
        MSG_END_RENTAL: "MSG_END_RENTAL",
        MSG_CAR_LIST: "MSG_CAR_LIST",
        ERR_SUCCESS: "ERR_SUCCESS",
        ERR_BAD_FORMAT: "ERR_BAD_FORMAT",
        ERR_INVALID_TYPE: "ERR_INVALID_TYPE",
        ERR_ALREADY_REGISTERED: "ERR_ALREADY_REGISTERED",
        ERR_NOT_REGISTERED: "ERR_NOT_REGISTERED",
        ERR_ALREADY_RENTED: "ERR_ALREADY_RENTED",
        ERR_NOT_RENTED: "ERR_NOT_RENTED",
        ERR_CAR_UNAVAILABLE: "ERR_CAR_UNAVAILABLE"
    }

    def __init__(self, bin_msg=None, user_id=0, msg_type=0, msg=""):
        if bin_msg is not None:
            if len(bin_msg) < 5:
                raise InvalidMessageError("Message too short")
            self.user_id, self.msg_type, self.msg_size = struct.unpack('>HbH', bin_msg[:5])
            self.msg = bin_msg[5:].decode('utf-8')
            print("Build binary message")
        else:
            self.user_id = user_id
            self.msg_type = msg_type

            self.msg_size = len(msg)
            self.msg = msg

    def to_binary(self):
        return struct.pack('>HbH', self.user_id, self.msg_type, self.msg_size) + self.msg.encode('utf-8')

    def __str__(self) -> str:
        return f"User ID: {self.user_id}\nMessage Type: {self.type_to_str[self.msg_type]}\nMessage Size: {self.msg_size}\nMessage: {self.msg}"
