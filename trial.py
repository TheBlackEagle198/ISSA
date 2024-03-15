import pygame
import socket
import sys
from config import *
from Message import Message

def draw_text(surface, text, pos, font, color):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def main():
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Car Sharing App")

    # Load the background images
    backgrounds = {
        "main": pygame.image.load("img/main.png").convert(),
        "menu": pygame.image.load("img/menu.png").convert(),
        "register": pygame.image.load("img/register.png").convert(),
        "thanks": pygame.image.load("img/thanks.png").convert(),
        "carlist": pygame.image.load("img/carlist.png").convert(),
        "ride": pygame.image.load("img/ride.png").convert()
    }

    # Set up fonts
    font = pygame.font.SysFont(None, 36)

    # Set up the socket connection
    s = socket.socket()
    port = backend_port
    s.connect(('localhost', port))
    user_id = int(sys.argv[1])

    clock = pygame.time.Clock()

    current_screen = "main"
    registering_car = False
    registering_text = ""

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                print("Mouse Position:", mouse_pos)
                if current_screen == "main":
                    current_screen = "menu"
                elif current_screen == "menu":
                    if 1200 <= mouse_pos[0] <= 1700 and 400 <= mouse_pos[1] <= 600:
                        current_screen = "register"
                    elif 1200 <= mouse_pos[0] <= 1700 and 700 <= mouse_pos[1] <= 900:
                        current_screen = "carlist"
                elif current_screen == "register":
                    if 1575 <= mouse_pos[0] <= 1775 and 700 <= mouse_pos[1] <= 1000:
                        # Send registration message
                        message = Message(user_id=user_id, msg_type=Message.MSG_REGISTER, msg=registering_text)
                        s.send(message.to_binary())
                        recv_msg = s.recv(1024)
                        print(Message(bin_msg=recv_msg))
                        current_screen = "thanks"
                elif current_screen == "thanks":
                    current_screen = "main"
                elif current_screen == "carlist":
                    # Request list of cars from server
                    message = Message(user_id=user_id, msg_type=Message.MSG_REQUEST_CARS)
                    s.send(message.to_binary())
                    recv_msg = s.recv(1024)
                    car_list = Message(bin_msg=recv_msg).msg  # Assuming the server responds with a list of cars

                    # Create buttons for each car
                    car_buttons = []
                    for i, car in enumerate(car_list):
                        button_rect = pygame.Rect(1175, 700 + i * 100, 600, 50)  # Adjust these values as needed
                        car_buttons.append(button_rect)
                        pygame.draw.rect(screen, (255, 255, 255), button_rect)
                        draw_text(screen, car, (1175, 700 + i * 100), font, (0, 0, 0))  # Adjust these values as needed

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for i, button_rect in enumerate(car_buttons):
                            if button_rect.collidepoint(mouse_pos):
                                # Send message to request ride
                                chosen_car = car_list[i]
                                message = Message(user_id=user_id, msg_type=Message.MSG_START_RENTAL, msg=chosen_car)
                                s.send(message.to_binary())
                                recv_msg = s.recv(1024)
                                print(Message(bin_msg=recv_msg))
                                current_screen = "ride"
                                break
                elif current_screen == "ride":
                    if 200 <= mouse_pos[0] <= 600 and 275 <= mouse_pos[1] <= 400:
                        # End ride button clicked
                        message = Message(user_id=user_id, msg_type=Message.MSG_END_RENTAL)
                        s.send(message.to_binary())
                        recv_msg = s.recv(1024)
                        print(Message(bin_msg=recv_msg))
                        current_screen = "thanks"

        # Draw the background
        screen.blit(backgrounds[current_screen], (0, 0))

        if current_screen == "register":
            # Draw registration text input box
            pygame.draw.rect(screen, (255, 255, 255), (1125, 800, 400, 100))
            draw_text(screen, registering_text, (1130, 810), font, (0, 0, 0))
            draw_text(screen, "Register", (1575, 700), font, (0, 0, 0))

        # Update the display
        pygame.display.flip()

        clock.tick(30)

    pygame.quit()

if __name__ == '__main__':
    main()
