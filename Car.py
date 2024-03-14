import socket
import sys
from config import *
from CarMessage import *
import threading
import pygame
import pyperclip


class CarServer(threading.Thread):
    def __init__(self, port=0) -> None:
        threading.Thread.__init__(self)
        self.port = port
        self.s = socket.socket()
        self.s.bind(('localhost', port))
        self.s.listen(5)

        print(f"Started server: {self.s.__str__()}")
        self.s.settimeout(1)
        self.is_rented = False
        self.exit_request = False

    def run(self):
        try:
            while True:
                try:
                    client_socket, address = self.s.accept()
                    print(f"Accepted connection from {address}")

                    raw_msg = client_socket.recv(1024)

                    msg = CarMessage(raw_msg=raw_msg)

                    match msg.message:
                        case CarMessage.MSG_START_RENTAL:
                            print("Starting rental...")

                            if self.is_rented:
                                client_socket.send(CarMessage(CarMessage.ERR_FAIL,
                                                            reason_code=CarMessage.REASON_ALREADY_RENTED).to_binary())
                            else:
                                self.is_rented = True
                                client_socket.send(CarMessage(CarMessage.ERR_SUCCESS).to_binary())
                        case CarMessage.MSG_END_RENTAL:
                            print("Ending rental...")

                            if not self.is_rented:
                                client_socket.send(
                                    CarMessage(CarMessage.ERR_FAIL, reason_code=CarMessage.REASON_NOT_RENTED).to_binary())
                            else:
                                self.is_rented = False
                                client_socket.send(CarMessage(CarMessage.ERR_SUCCESS).to_binary())
                        case CarMessage.MSG_PING:
                            print("Responding to ping...")
                            client_socket.send(CarMessage(CarMessage.ERR_SUCCESS).to_binary())
                        case _:
                            print("Invalid message type!")
                            client_socket.send(CarMessage(CarMessage.ERR_FAIL).to_binary())

                    client_socket.close()
                except TimeoutError:
                    if self.exit_request:
                        print("Exiting server...")
                        break
        except KeyboardInterrupt:
            print("Closing server...")
        finally:
            self.s.close()


    def get_car_info(self):
        return f"{self.s.getsockname()[0]}:{self.s.getsockname()[1]}"

class MainView:
    def __init__(self, screen, font) -> None:
        self.screen = screen
        self.font = font
        self.info_btn = None

    def draw(self, is_rented: bool, car_info: str):
        self.screen.fill(pygame.Color("green") if is_rented else pygame.Color("red"))
        
        info_text = f"Car: {car_info}"
        info = self.font.render(info_text, True, (255, 255, 255))

        avl_text = "You can drive the car" if is_rented else "Car is available for rental"
        avl = self.font.render(avl_text, True, (255, 255, 255))

        # Compute the center of the screen for the first line of text.
        center_info_x = (self.screen.get_width() - info.get_width()) // 2
        center_info_y = (self.screen.get_height() - info.get_height()) // 2

        # Compute the position for the second line of text.
        center_avl_x = (self.screen.get_width() - avl.get_width()) // 2
        center_avl_y = center_info_y + avl.get_height()

        # Blit the text surfaces onto the screen.
        self.screen.blit(avl, (center_avl_x, center_avl_y))
        self.screen.blit(info, (center_info_x, center_info_y))

        self.info_btn = pygame.Rect(center_info_x, center_info_y, info.get_width(), info.get_height())

        pygame.display.flip()

def main():
    print("Starting car server...")
    car_server = CarServer()
    car_server.start()

    print("Starting pygame...")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(f"Car {car_server.get_car_info()}")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    main_view = MainView(screen, font)

    last_car_state = not car_server.is_rented

    should_stop_gui = False
    try:
        while not should_stop_gui:
            if not car_server.is_alive():
                should_stop_gui = True
                continue
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        should_stop_gui = True
                        break
                    case pygame.MOUSEBUTTONDOWN:
                        if main_view.info_btn:
                            if main_view.info_btn.collidepoint(event.pos):
                                print("Info button clicked!")
                                pyperclip.copy(car_server.get_car_info())
            if last_car_state != car_server.is_rented:
                last_car_state = car_server.is_rented
                main_view.draw(last_car_state, car_server.get_car_info().__str__())
            clock.tick(30)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        print("Exiting GUI...")
        car_server.exit_request = True
        car_server.join()

if __name__ == '__main__':
    main()
