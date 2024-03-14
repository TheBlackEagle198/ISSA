import socket
import threading
from config import *
from Message import *
from CarMessage import *

class AlreadyRegisteredError(Exception):
	def __init__(self, message):
		super().__init__(message)
class NotRegisteredError(Exception):
	def __init__(self, message):
		super().__init__(message)
class NotRentedError(Exception):
	def __init__(self, message):
		super().__init__(message)
class AlreadyRentedError(Exception):
	def __init__(self, message):
		super().__init__(message)
class CarUnavailable(Exception):
	def __init__(self, message):
		super().__init__(message)

class CarEntity:
	"""A class to represent a car entity.
	"""
	def __init__(self, raw_msg = None, addr = '', port = 0):
		if raw_msg is not None:
			self.addr = raw_msg.split(':')[0]
			self.port = int(raw_msg.split(':')[1])
		else:
			self.addr = addr
			self.port = port
		self.rented = False
		self.id = hash(self)

	def __hash__(self) -> int:
		return hash(self.addr + str(self.port))

class ClientHandler(threading.Thread):
	"""A class to handle an App client connection to the backend server.
	"""
	def __init__(self, client_socket, car_db):
		threading.Thread.__init__(self)
		self.client_socket = client_socket
		self.car_db = car_db
		self.finished = False
		self.exit_request = False

	def run(self):
		"""The client handler thread.
		"""
		try:
			self.client_socket.settimeout(1)
			while True:
				try:
					binary_msg = self.client_socket.recv(1024)
					print(binary_msg)
					request_msg = Message(bin_msg=binary_msg)
					print("Received: " + request_msg.__str__())
					match request_msg.msg_type:
						case Message.MSG_REGISTER:
							self.register(request_msg.msg)
						case Message.MSG_REQUEST_CARS:
							self.request_cars()
						case Message.MSG_START_RENTAL:
							self.start_rent(request_msg.msg)
						case Message.MSG_END_RENTAL:
							self.end_rent(request_msg.msg)
						case _:
							raise InvalidMessageTypeError("Invalid message type")
				except TimeoutError:
					if self.exit_request:
						break
				except InvalidMessageError as e:
					print("Invalid message received: " + str(e))
					self.client_socket.send(Message(msg_type = Message.ERR_BAD_FORMAT).to_binary())
				except InvalidMessageTypeError as e:
					print("Invalid message type received: " + str(e))
					self.client_socket.send(Message(msg_type = Message.ERR_INVALID_TYPE).to_binary())
				except AlreadyRegisteredError as e:
					print("Car already registered: " + str(e))
					self.client_socket.send(Message(msg_type = Message.ERR_ALREADY_REGISTERED).to_binary())
				except NotRegisteredError as e:
					print("Car not registered: " + str(e))
					self.client_socket.send(Message(msg_type = Message.ERR_NOT_REGISTERED).to_binary())
				except AlreadyRentedError as e:
					print("Car already rented: " + str(e))
					self.client_socket.send(Message(msg_type = Message.ERR_ALREADY_RENTED).to_binary())
				except NotRentedError as e:
					print("Car not rented: " + str(e))
					self.client_socket.send(Message(msg_type = Message.ERR_NOT_RENTED).to_binary())
				except CarUnavailable as e:
					print("Car unavailable: " + str(e))
					self.client_socket.send(Message(msg_type = Message.ERR_CAR_UNAVAILABLE).to_binary())
		except (BrokenPipeError, ConnectionResetError) as e:
			print(f"Client {str(self.client_socket)} disconnected!, " + str(e))
		finally:
			self.client_socket.close()
			self.finished = True

	def register(self, car_info : str) -> None:
		"""Register a car with the backend.
		:param car_info: str the car to register
		"""
		print("Registering car...")
		if len(car_info) == 0:
			raise InvalidMessageError("Empty car info")
		curr_car = CarEntity(raw_msg=car_info)

		car_msg = self.send_to_car(curr_car, CarMessage(CarMessage.MSG_PING))
		if car_msg.message == CarMessage.ERR_SUCCESS:
			self.car_db.add(curr_car)
			self.client_socket.send(Message(msg_type=Message.ERR_SUCCESS).to_binary())
		else:
			raise CarUnavailable("Car is not available")

	def request_cars(self) -> None:
		"""Request a list of all cars.
		"""
		print("Requesting cars...")
		cars = self.car_db.get_all()

		payload = ''.join([f"{car[1].addr}:{car[1].port}\n" for car in cars])

		msg = Message(msg_type=Message.MSG_CAR_LIST, msg=payload)
		self.client_socket.send(msg.to_binary())
		print("Done!")

	def start_rent(self, car_info : str) -> None:
		"""Start a rental for a car.
		:param car_info: str the car to start the rental for
		"""
		print("Starting rental...")
		curr_car = self.car_db.get(hash(CarEntity(raw_msg=car_info)))

		if curr_car is None:
			raise NotRegisteredError("Car not found")

		if curr_car.rented:
			raise AlreadyRentedError("Car is already rented")

		# send start rental message to car
		car_msg = self.send_to_car(curr_car, CarMessage(CarMessage.MSG_START_RENTAL))
		if car_msg.message == CarMessage.ERR_SUCCESS:
			curr_car.rented = True
			self.client_socket.send(Message(msg_type=Message.ERR_SUCCESS).to_binary())
		else:
			if car_msg.reason_code == CarMessage.REASON_ALREADY_RENTED:
				curr_car.rented = True
				raise AlreadyRentedError("Car is already rented")
			raise CarUnavailable("Car is not available")

	def end_rent(self, car_info : str) -> None:
		"""End a rental for a car.
		:param car_info: str the car to end the rental for
		"""
		print("Ending rental...")
		curr_car = self.car_db.get(hash(CarEntity(raw_msg=car_info)))

		if curr_car is None:
			raise NotRegisteredError("Car not found")
		
		if not curr_car.rented:
			raise NotRentedError("Car is not rented")

		# send end rental message to car
		car_msg = self.send_to_car(curr_car, CarMessage(CarMessage.MSG_END_RENTAL))
		if car_msg.message == CarMessage.ERR_SUCCESS:
			curr_car.rented = False
			self.client_socket.send(Message(msg_type = Message.ERR_SUCCESS).to_binary())
		else:
			if car_msg.reason_code == CarMessage.REASON_NOT_RENTED:
				curr_car.rented = False
				raise NotRentedError("Car is not rented")
			raise CarUnavailable("Car is not available")

	def send_to_car(self, car : CarEntity, msg : CarMessage) -> CarMessage:
		"""Send a message to a car and return the response message.
		:param car: CarEntity the car to send the message to
		:param msg: CarMessage the message to send
		"""
		result = CarMessage(CarMessage.ERR_FAIL, CarMessage.REASON_NONE)
		try:
			s = socket.socket()
			s.connect((car.addr, car.port))
			s.send(msg.to_binary())

			s.settimeout(2)
			raw_msg = s.recv(1024)
			result = CarMessage(raw_msg=raw_msg)

			s.close()
		except (ConnectionRefusedError, TimeoutError) as e:
			print("Car is not available!")
		return result

class CarDB:
	"""A class to represent a car database.
	"""
	def __init__(self):
		self.cars = dict()

	def add(self, car):
		if self.get(car.id) is not None:
			raise AlreadyRegisteredError("Car is already in the database!")
		self.cars[car.id] = car

	def remove(self, car):
		del self.cars[car.id]

	def get(self, car_id):
		try:
			return self.cars[car_id]
		except KeyError:
			return None
	
	def get_all(self):
		return self.cars.items()

def main():
	"""The main function.
	Spawns multiple handlers for App client connections.
	Takes care of joining finished client handlers.
	"""
	s = socket.socket()
	s.bind(('localhost', backend_port))
	s.listen(5)
	s.settimeout(1)
	cars = CarDB()
	print("Server is listening...")
	handlers = []
	try:
		while True:
			try:
				client_socket, address = s.accept()
				print("Accepted connection from " + str(address))
				handlers.append(ClientHandler(client_socket, cars))
				handlers[-1].start()
			except TimeoutError:
				# join finished client handlers
				for handler in handlers:
					if handler.finished:
						print("Joining finished client handler...")
						handler.join()
						handlers.remove(handler)
	except KeyboardInterrupt:
		print("Closing server...")
		for handler in handlers:
			handler.exit_request = True
		while len(handlers) > 0:
			for handler in handlers:
				if handler.finished:
					print("Joining finished client handler...")
					handler.join()
					handlers.remove(handler)
	finally:
		s.close()

if __name__ == '__main__':
	main()