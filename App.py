import pygame
import socket
import sys
from config import *
from Message import Message

def main():
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Mouse Position Tracker")

    # Load the background image
    background = pygame.image.load("img/main.png").convert()

    # Set up the socket connection
    s = socket.socket()
    port = backend_port
    s.connect(('localhost', port))
    user_id = int(sys.argv[1])

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                print("Mouse Position:", mouse_pos)

        # Draw the background
        screen.blit(background, (0, 0))

        # Update the display
        pygame.display.flip()

        # Send message to the server
        console_input = input("-> ")
        params = console_input.split()

        message = Message(user_id=user_id)

        if params:
            if params[0].lower() == "exit":
                s.close()
                running = False
            elif params[0].lower() == "register":
                message.msg_type = Message.MSG_REGISTER
                message.msg = params[1] if len(params) > 1 else ""
            elif params[0].lower() == "request_cars":
                message.msg_type = Message.MSG_REQUEST_CARS
            elif params[0].lower() == "start_rental":
                message.msg_type = Message.MSG_START_RENTAL
                message.msg = params[1] if len(params) > 1 else ""
            elif params[0].lower() == "end_rental":
                message.msg_type = Message.MSG_END_RENTAL
                message.msg = params[1] if len(params) > 1 else ""
            elif params[0].lower() == "bad_message_type":
                message.msg_type = 100
            else:
                print("Invalid command!")

            s.send(message.to_binary())
            recv_msg = s.recv(1024)
            print(Message(bin_msg=recv_msg))

        clock.tick(30)  # Limit frame rate to 30 FPS

    pygame.quit()

if __name__ == '__main__':
    main()
