import socket
from config import *
from Message import Message
import sys


def main():
    s = socket.socket()

    port = backend_port

    s.connect(('localhost', port))

    user_id = int(sys.argv[1])

    while True:
        # message you send to the server
        console_input = input("-> ")

        params = console_input.split()

        message = Message(
            user_id=user_id
        )

        match params[0].lower():
            case "exit":
                s.close()
                break
            case "register":
                message.msg_type = Message.MSG_REGISTER
                message.msg = params[1]
            case "request_cars":
                message.msg_type = Message.MSG_REQUEST_CARS
            case "start_rental":
                message.msg_type = Message.MSG_START_RENTAL
                message.msg = params[1]
            case "end_rental":
                message.msg_type = Message.MSG_END_RENTAL
                message.msg = params[1]
            case "bad_message_type":
                message.msg_type = 100
            case _:
                print("Invalid command!")
                continue

        s.send(message.to_binary())

        recv_msg = s.recv(1024)
        print(Message(bin_msg=recv_msg))


if __name__ == '__main__':
    main()
