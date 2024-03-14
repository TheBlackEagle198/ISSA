import socket
import sys
from config import *
from CarMessage import *


def main():
    if len(sys.argv) < 2:
        port = 0
    else:
        port = int(sys.argv[1])
    s = socket.socket()
    s.bind(('localhost', port))
    s.listen(5)

    print(f"Started server: {s.__str__()}")
    s.settimeout(1)

    is_rented = False
    try:
        while True:
            try:
                client_socket, address = s.accept()
                print(f"Accepted connection from {address}")

                raw_msg = client_socket.recv(1024)

                msg = CarMessage(raw_msg=raw_msg)

                match msg.message:
                    case CarMessage.MSG_START_RENTAL:
                        print("Starting rental...")

                        if is_rented:
                            client_socket.send(CarMessage(CarMessage.ERR_FAIL,
                                                          reason_code=CarMessage.REASON_ALREADY_RENTED).to_binary())
                        else:
                            is_rented = True
                            client_socket.send(CarMessage(CarMessage.ERR_SUCCESS).to_binary())
                    case CarMessage.MSG_END_RENTAL:
                        print("Ending rental...")

                        if not is_rented:
                            client_socket.send(
                                CarMessage(CarMessage.ERR_FAIL, reason_code=CarMessage.REASON_NOT_RENTED).to_binary())
                        else:
                            is_rented = False
                            client_socket.send(CarMessage(CarMessage.ERR_SUCCESS).to_binary())
                    case CarMessage.MSG_PING:
                        print("Responding to ping...")
                        client_socket.send(CarMessage(CarMessage.ERR_SUCCESS).to_binary())
                    case _:
                        print("Invalid message type!")
                        client_socket.send(CarMessage(CarMessage.ERR_FAIL).to_binary())

                client_socket.close()
            except TimeoutError:
                pass
    except KeyboardInterrupt:
        print("Closing server...")
        s.close()


if __name__ == '__main__':
    main()
