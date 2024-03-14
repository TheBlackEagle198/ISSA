import struct


class CarMessage:
    MSG_START_RENTAL = 0
    MSG_END_RENTAL = 1
    MSG_PING = 2

    ERR_SUCCESS = 3
    ERR_FAIL = 4

    REASON_NONE = 0
    REASON_ALREADY_RENTED = 1
    REASON_NOT_RENTED = 2

    def __init__(self, msg_type=MSG_PING, reason_code=REASON_NONE, raw_msg=None):
        if raw_msg is not None:
            self.message, self.reason_code = struct.unpack('>bb', raw_msg)
        else:
            self.message = msg_type
            self.reason_code = reason_code

    def to_binary(self):
        """Convert the message to a binary format.
        """
        return struct.pack('>bb', self.message, self.reason_code)
