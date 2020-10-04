import socket
import pygame
import pygame.freetype
import util
import pickle

FORMAT = 'utf-8'
pygame.init()


def get_username(win, first, font):
    """
    Use a pygame window to receive requested username from keyboard input.
    :param win: pygame window
    :type win: pygame.Surface
    :param first: is it the first time entering the function
    :type first: bool
    :param font: file-like object representing the font
    :type font: io.BytesIO
    :return: requested username
    :rtype: str
    """
    username = ''
    run = True
    question_font = pygame.freetype.Font(font, 60)
    print()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:  # Keypress
                if event.key == pygame.K_BACKSPACE:  # Backspace
                    username = username[:-1]  # Remove the last char of username
                elif event.key == pygame.K_RETURN:  # Enter key
                    run = False  # Stop the loop and return the username
                else:
                    if util.is_english(event.unicode):  # The char is in English
                        username = username + event.unicode
                    else:  # The char is not English (so it must be Hebrew?)
                        username = event.unicode + username
            elif event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # Draw the screen
        win.fill((0, 0, 0))  # Black background
        text_surface, rect = question_font.render(username, (0, 0, 0))  # Save the text in black
        *_, w, h = rect
        pygame.draw.rect(win, (255, 255, 255), (456, 285, 600, 100), 0)  # White "textbox"
        # Blit the text to the center of the "textbox"
        win.blit(text_surface, (int(456 + ((600 / 2) - (w / 2))), int(285 + ((100 / 2) - (h / 2)))))
        text = 'בחר שם משתמש'[::-1] if first else 'השם הזה כבר תפוס.'[::-1]  # Instruction text (reversed)
        text_surface, rect = question_font.render(text, (255, 255, 255))  # Save it in white
        *_, w, h = rect
        # Blit the text above the "textbox"
        win.blit(text_surface, (int(456 + ((600 / 2) - (w / 2))), int(285 - 10 - h)))
        # Push everything to the display
        pygame.display.update()
    return username


class Network:
    def __init__(self, win):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Host IPv4 and Port defined in server.py
        self.host = "10.0.0.33"
        self.port = 5050
        self.addr = (self.host, self.port)
        self.client.connect(self.addr)  # Connect to the server
        reply = self.client.recv(100000)  # receive ~100KiB of the font and background image from the server
        reply = pickle.loads(reply)
        self.bg_image = reply.image
        self.font = reply.font
        invalid = True
        first = True
        # Get username:
        while invalid:
            self.id = get_username(win, first, reply.font)
            response = self.send('username')
            if not response.OK:
                first = False
            else:
                invalid = False
                self.color = response.color
                self.id = f'{self.id}:{self.color}'

    def send(self, t, data=None):
        """
        Send information to the server.
        :param data: Info about the answer of the player (time and chosen answer)
        :type data: dict
        :param t: type
        :type t: str
        :return: a pickle object of the server's reply
        :rtype: Response
        """
        if t == 'username':
            msg = util.Response('username')
            msg.username = self.id
        elif t == 'get':
            msg = util.Response('get')
        elif t == 'post':
            msg = util.Response('post')
            msg.time = data["time"]
            msg.answer = data["answer"]
            msg.username = self.id
        elif t == 'disconnect':
            msg = util.Response('disconnect')
        else:
            msg = False

        msg = pickle.dumps(msg)
        self.client.send(msg)
        reply = self.client.recv(2048)
        reply = pickle.loads(reply)
        return reply

