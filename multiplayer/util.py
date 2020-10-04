"""Utilities for the server and client."""
import pygame
import pygame.freetype
import logging
import time


class Response:
    """
    A response for server-client communication.
    Other instance attributes are added to the class where necessary.
    """
    def __init__(self, t):
        """
        :param t: type of response
        """
        self.type = t


def is_english(s):
    """Test if a string contains only ASCII characters (English)
    :param s: string to test
    :type s: str
    :return: The string contains / not contains non-ASCII characters
    :rtype: bool
    """
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False  # The string contains one character or more that are not ASCII
    else:
        return True  # The string only contains ASCII


def log(sender, msg):
    output = f"[{sender.upper()}] {msg}"
    print(f"<{time.strftime('%H:%M:%S', time.localtime())}> {output}")
    logging.info(output)


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
    while run:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:  # Keypress
                if event.key == pygame.K_BACKSPACE:  # Backspace
                    username = username[:-1]  # Remove the last char of username
                elif event.key == pygame.K_RETURN:  # Enter key
                    run = False  # Stop the loop and return the username
                else:
                    if is_english(event.unicode):  # The char is in English
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
