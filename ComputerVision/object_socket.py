import socket
import select
import pickle
import datetime

from typing import *


class ObjectSocketParams:
    """Wrapper for configuration constants"""
    OBJECT_HEADER_SIZE_BYTES = 4
    DEFAULT_TIMEOUT_S = 1
    CHUNK_SIZE_BYTES = 1024


class ObjectSenderSocket:
    """Sends objects to a receiver socket. Uses pickle to serialize the objects.
    
    Attributes:
        ip: str -- The IP of the receiver socket.
        port: int -- The port of the receiver socket.
        sock: socket.socket -- The socket used to send the objects.
        conn: socket.socket -- The connection socket.
        print_when_awaiting_receiver: bool -- Whether to print when awaiting the receiver.
        print_when_sending_object: bool -- Whether to print when sending an object.
    
    Methods:
        await_receiver_conection() -- Awaits the receiver connection.
        close() -- Closes the connection.
        is_connected() -> bool -- Returns whether the connection is active.
        send_object(obj: Any) -- Sends an object to the receiver socket.
    """
    ip: str
    port: int
    sock: socket.socket
    conn: socket.socket
    print_when_awaiting_receiver: bool
    print_when_sending_object: bool

    def __init__(self, ip: str, port: int,
                 print_when_awaiting_receiver: bool = False,
                 print_when_sending_object: bool = False):
        """Initializes the ObjectSenderSocket and awaits the receiver connection.

        Args:
            ip: str -- The IP of the receiver socket.
            port: int -- The port of the receiver socket.
            print_when_awaiting_receiver = False: bool -- Whether to print when awaiting the receiver.
            print_when_sending_object = False: bool -- Whether to print when sending an object.
        """
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.conn = None

        self.print_when_awaiting_receiver = print_when_awaiting_receiver
        self.print_when_sending_object = print_when_sending_object

        self.await_receiver_conection()

    def await_receiver_conection(self):
        """Blocking function which waits the receiver connection.

        Prints a message if print_when_awaiting_receiver is True.
        """
        if self.print_when_awaiting_receiver:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] awaiting receiver connection...')

        self.sock.listen(1)
        self.conn, _ = self.sock.accept()

        if self.print_when_awaiting_receiver:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] receiver connected')

    def close(self):
        """Closes the connection."""
        self.conn.close()
        self.conn = None

    def is_connected(self) -> bool:
        """Returns whether the connection is active.
        
        Returns:
            bool -- True if the connection is active, false otherwise.
        """
        return self.conn is not None

    def send_object(self, obj: Any):
        """Sends an object to the receiver socket.

        The object is serialized using pickle.
        Also prints a message if print_when_sending_object is True.

        Args:
            obj: Any -- The object to send.
        """
        data = pickle.dumps(obj)
        data_size = len(data)
        data_size_encoded = data_size.to_bytes(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES, 'little')
        self.conn.sendall(data_size_encoded)
        self.conn.sendall(data)
        if self.print_when_sending_object:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] Sent object of size {data_size} bytes.')


class ObjectReceiverSocket:
    """Receives objects from a sender socket. Uses pickle to deserialize the objects.
    
    Attributes:
        ip: str -- The IP of the sender socket.
        port: int -- The port of the sender socket.
        conn: socket.socket -- The connection socket.
        print_when_connecting_to_sender: bool -- Whether to print when connecting to the sender.
        print_when_receiving_object: bool -- Whether to print when receiving an object.
    
    Methods:
        connect_to_sender() -- Connects to the sender socket.
        close() -- Closes the connection.
        is_connected() -> bool -- Returns whether the connection is active.
        recv_object() -> Any -- Receives an object from the sender socket.
    """
    ip: str
    port: int
    conn: socket.socket
    print_when_connecting_to_sender: bool
    print_when_receiving_object: bool

    def __init__(self, ip: str, port: int,
                 print_when_connecting_to_sender: bool = False,
                 print_when_receiving_object: bool = False):
        """Initializes the ObjectReceiverSocket and initiates the connection to the sender socket.
        
        Args:
            ip: str -- The IP of the sender socket.
            port: int -- The port of the sender socket.
            print_when_connecting_to_sender = False: bool -- Whether to print when connecting to the sender.
            print_when_receiving_object = False: bool -- Whether to print when receiving an object.
        """
        self.ip = ip
        self.port = port
        self.print_when_connecting_to_sender = print_when_connecting_to_sender
        self.print_when_receiving_object = print_when_receiving_object

        self.connect_to_sender()

    def connect_to_sender(self):
        """Connects to the sender socket.
        
        Prints a message if print_when_connecting_to_sender is True.

        Returns:
            None
        """

        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connecting to sender...')

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))

        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connected to sender')

    def close(self):
        """Closes the connection.

        Returns:
            None
        """
        self.conn.close()
        self.conn = None

    def is_connected(self) -> bool:
        """Returns whether the connection is active.

        Returns:
            bool -- True if the connection is active, false otherwise.
        """
        return self.conn is not None

    def recv_object(self) -> Any:
        """Receives an object from the sender socket and deserializes it.
        
        Also prints a message if print_when_receiving_object is True.

        Returns:
            Any -- The object received.
        """
        obj_size_bytes = self._recv_object_size()
        data = self._recv_all(obj_size_bytes)
        obj = pickle.loads(data)
        if self.print_when_receiving_object:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] Received object of size {obj_size_bytes} bytes.')
        return obj

    def _recv_with_timeout(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> Optional[bytes]:
        rlist, _1, _2 = select.select([self.conn], [], [], timeout_s)
        if rlist:
            data = self.conn.recv(n_bytes)
            return data
        else:
            return None  # Only returned on timeout

    def _recv_all(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> bytes:
        data = []
        left_to_recv = n_bytes
        while left_to_recv > 0:
            desired_chunk_size = min(ObjectSocketParams.CHUNK_SIZE_BYTES, left_to_recv)
            chunk = self._recv_with_timeout(desired_chunk_size, timeout_s)
            if chunk is not None:
                data += [chunk]
                left_to_recv -= len(chunk)
            else:  # no more data incoming, timeout
                bytes_received = sum(map(len, data))
                raise socket.error(f'Timeout elapsed without any new data being received. '
                                   f'{bytes_received} / {n_bytes} bytes received.')
        data = b''.join(data)
        return data

    def _recv_object_size(self) -> int:
        data = self._recv_all(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES)
        obj_size_bytes = int.from_bytes(data, 'little')
        return obj_size_bytes