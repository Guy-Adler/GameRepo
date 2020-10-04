import pygame
import pygame.freetype
from network import Network
import random
import math

pygame.init()

PI = math.pi


class Board:
    """
    Stores the background of the window, and all the cells of the board
    """
    def __init__(self, window, font, image):
        """
        :param window: pygame window
        :type window: pygame.Surface
        :param font: The font to use
        :type font: pygame.freetype.Font
        :param image: The image to use as background
        :type image: io.BytesIO
        """
        self.win = window
        self.image = pygame.image.load(image)  # Load the image
        self.image_rect = self.image.get_rect()
        self.font = font
        self.cells = []

    def draw(self):
        """
        Blit the image to the screen
        """
        self.win.blit(self.image, self.image_rect)

    def create_cells(self):
        """
        Create all of the cells and sort them to match the board.
        """
        count = 1
        for i in range(10):
            temp = []
            for j in range(10):
                temp.append(Cell(self.win, (j * 77, i * 77, 77, 77), self.font))  # Cells are 77 * 77 px
                count += 1
            self.cells.append(temp)

        self.cells = self.cells[::-1]  # make the cells go from the bottom to the top
        temp = []
        for index, row in enumerate(self.cells):
            temp.extend(row if index % 2 == 0 else row[::-1])  # make the cells go ltr or rtl, depending on the row.
        self.cells = temp
        for i, c in enumerate(self.cells):
            c.num = str(i + 1)  # number the cells correctly


class Cell:
    """
    A rect that matches the board image's cell. Each instance has a unique number, printed in the top-left of the cell.
    """
    def __init__(self, window, pos, font):
        """
        :param window: pygame window
        :type window: pygame.Surface
        :param pos: (x, y, w, h); x and y of the wop left of the cell, w and h are width and height.
        :type pos: tuple
        :param font: The font to use
        :type font: pygame.freetype.FONT
        """
        self.x, self.y, self.width, self.height = pos
        self.win = window
        self.num = '0'  # will be changed later in Board.create_cells()
        self.font = font

    def draw(self):
        """
        Blit the number of the cell to the top left of the cell, with some padding (10px)
        """
        self.font.size = 20
        self.font.render_to(self.win, (self.x + 10, self.y + 10), self.num, (0, 0, 0))


class Player:
    """
    A circle on the board.
    """
    def __init__(self, window, color, pos):
        """
        :param window: pygame window
        :type window: pygame.Surface
        :param color: a list (or a string representation of it), in format [R, G, B] (0 <= R, G, B <= 255)
        :type color: list
        :param pos: (x, y, r); x and y are the middle of the circle, r is the radius.
        :type pos: tuple
        """
        self.x, self.y, self.r = pos
        self.win = window
        self.color = color
        if type(self.color) == str:  # sometimes funny things happen...
            self.color = eval(self.color)

    def draw(self):
        """
        Draw the player.
        """
        pygame.draw.circle(self.win, self.color, (self.x, self.y), self.r)


class Question:
    """
    The place where questions are displayed.
    """
    def __init__(self, window, font):
        """
        :param window: pygame window
        :type window: pygame.Surface
        :param font: The font to use
        :type font: pygame.freetype.FONT
        """
        self.win = window
        self.question = ''  # will be change later
        self.pos = (874, 0, 520, 378)  # The bounding box of the question, on the board image.
        self.font = font

    def draw(self):
        """
        Blit the question to the center of the bounding box.
        """
        self.font.size = 60
        text_surface, rect = self.font.render(str(self.question), (0, 0, 0))
        *_, w, h = rect
        rect = (int(self.pos[0] + ((self.pos[2] / 2) - (w / 2))), int(self.pos[1] + ((self.pos[3] / 2) - (h / 2))))
        self.win.blit(text_surface, rect)


class Answers:
    """
    The place where answers are displayed.
    """
    def __init__(self, window, font):
        """
        :param window: pygame window
        :type window: pygame.Surface
        :param font: The font to use
        :type font: pygame.freetype.FONT
        """
        self.win = window
        self.answers = ['' for _ in range(4)]  # will be changed later.
        self.pos = [(800, 378, 296, 151),  # red
                    (800, 567, 296, 151),  # yellow
                    (1172, 567, 296, 151),  # green
                    (1172, 378, 296, 151)]  # blue
        self.font = font

    def draw(self):
        """
        Blit all of the possible answers to the center of their bounding box
        """
        for index, answer in enumerate(self.answers):
            self.font.size = 40
            text_surface, rect = self.font.render(str(answer), (0, 0, 0))
            *_, w, h = rect
            box_x, box_y, box_w, box_h = self.pos[index]
            rect = (int(box_x + ((box_w / 2) - (w / 2))), int(box_y + ((box_h / 2) - (h / 2))))
            self.win.blit(text_surface, rect)


class Client:
    def __init__(self, win):
        """
        The main class that runs the game.
        :param win: pygame window
        :type win: pygame.Surface
        """
        self.window = win
        self.w = 1512  # Width of the window
        self.h = 770  # Height of the window
        self.net = Network(self.window)  # Create the network that communicates with the server
        self.FONT = pygame.freetype.Font(self.net.font)  # setup the font
        self.board = Board(self.window, self.FONT, self.net.bg_image)  # The main board (background image)
        self.board.create_cells()  # Create the cells in the board
        self.question = Question(self.window, self.FONT)  # The place for the questions
        self.answer = Answers(self.window, self.FONT)  # The place for the answers
        # Calculate the center of the first cell (index 0):
        x = int(self.board.cells[0].x + self.board.cells[0].width / 2)
        y = int(self.board.cells[0].y + self.board.cells[0].height / 2)
        self.r = 20  # Constant, The radius of the player
        self.players = {self.net.id: Player(self.window, self.net.color, (x, y, self.r))}  # Will be filled later.
        self.time = 0  # The time (seconds) it took to answer the question; Will be changed later
        self.correct = True  # Whether the answer was correct or not; Will be changed later.
        self.darker = pygame.Surface((self.w, self.h))  # The surface used when darkening the screen.
        self.darker.set_alpha(90)
        self.won = False
        self.answered = False

    def send(self, t, data=None):
        """
        Send data to the server via the network
        :param t: type of request
        :type t: str
        :param data: data about the answer (time it took to answer and the answer)
        :type data: dict
        :return: server reply
        :rtype: Response
        """
        reply = self.net.send(t, data)
        return reply

    def draw(self):
        """Draw the current screen"""
        self.board.draw()
        [cell.draw() for cell in self.board.cells]
        [player.draw() for player in self.players.values()]
        self.question.draw()
        self.answer.draw()
        pygame.draw.circle(self.window, self.net.color, (1133, 329), 38)
        pygame.display.update()

    def run(self):
        """The main loop of the game"""
        run = True
        message = ''
        while run:
            pygame.time.delay(100)
            reply = self.send('get')
            for player, score in reply.score.items():
                player_score = score if type(score) is int else 100
                x = int(self.board.cells[player_score - 1].x + self.board.cells[player_score - 1].width / 2)
                y = int(self.board.cells[player_score - 1].y + self.board.cells[player_score - 1].height / 2)
                if player in self.players:
                    self.players[player].x = x
                    self.players[player].y = y
                else:
                    self.players[player] = Player(self.window, player.split(':')[1], (x, y, self.r))
                self.won = True if type(reply.score[self.net.id]) is str else False

            if not reply.ready:
                self.draw()
                self.darker.fill((0, 0, 0))
                self.window.blit(self.darker, (0, 0))
                text = 'המשחק יתחיל כששחקן נוסף יצטרף...'[::-1]
                self.FONT.size = 60
                text_surface, rect = self.FONT.render(text, (0, 0, 255))
                *_, w, h = rect
                rect = (int(self.w / 2 - w / 2), int(self.h / 2 - (h + 200) / 2))
                self.window.blit(text_surface, rect)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        break
            elif not self.won and not self.answered:
                message = ''
                if not all(str(answer) for answer in self.answer.answers) or reply.question != self.question.question:
                    self.answer.answers = random.sample(list(reply.answers.keys()), 4)
                self.question.question = reply.question
                self.draw()
                pygame.draw.arc(self.window, (0, 0, 0),
                                (1133 - 38 - 10, 329 - 38 - 10, 2 * 38 + 20, 2 * 38 + 20), PI / 2,
                                ((2 * PI) / reply.duration) * reply.time_left + PI / 2, 10)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        break
                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()
                        self.time = reply.duration - reply.time_left
                        for index, rect in enumerate(self.answer.pos):
                            if rect[0] <= pos[0] <= rect[0] + rect[2] and rect[1] <= pos[1] <= rect[1] + rect[3]:
                                self.correct = self.send('post', {"time": self.time,
                                                                  "answer": self.answer.answers[index]})
                                self.answered = True
                                with open('answers.txt', 'a', encoding='utf-8') as f:
                                    f.write(f'{reply.question}: {self.answer.answers[index]} ({self.correct})\n')
            elif not self.won and self.answered:
                if reply.question != self.question.question:
                    self.answered = False
                    self.answer.answers = ['' for _ in range(4)]
                    continue
                self.draw()
                self.darker.fill((0, 0, 0))
                self.window.blit(self.darker, (0, 0))
                if self.correct:
                    message = "נכון, כל הכבוד!"
                    self.FONT.size = 60
                    text_surface, rect = self.FONT.render(message[::-1], (0, 255, 0))
                    *_, w, h = rect
                    rect = (int(self.w / 2 - w / 2), int(self.h / 2 - (h + 200) / 2 - 30))
                    self.window.blit(text_surface, rect)
                else:
                    possible = ["לא נורא, נסה שוב בפעם הבאה", "כל הכבוד על הנסיון, בפעם הבאה תצליח יותר"]
                    message = random.choice(possible) if not message else message
                    self.FONT.size = 60
                    text_surface, rect = self.FONT.render(message[::-1], (255, 0, 0))
                    *_, w, h = rect
                    rect = (int(self.w / 2 - w / 2), int(self.h / 2 - (h + 200) / 2 - 30))
                    self.window.blit(text_surface, rect)
                text = ' שניות'[::-1] + str(reply.time_left) + ' ' + 'בעוד '[::-1] + 'ממשיכים '[::-1]
                self.FONT.size = 60
                text_surface, rect = self.FONT.render(text, (0, 0, 255))
                *_, w, h = rect
                rect = (int(self.w / 2 - w / 2), int(398))
                self.window.blit(text_surface, rect)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        break
            elif self.won:
                self.draw()
                self.darker.fill((0, 0, 0))
                self.window.blit(self.darker, (0, 0))
                text = f'!{reply.score[self.net.id]}' + 'ה'[::-1] + ' ' + 'במקום'[::-1] + ' ' + 'סיימת'[::-1]
                text += ' ,' + 'הכבוד'[::-1] + ' ' + 'כל'[::-1]
                self.FONT.size = 60
                text_surface, rect = self.FONT.render(text, (0, 0, 255))
                *_, w, h = rect
                rect = (int(self.w / 2 - w / 2), int(self.h / 2 - (h + 200) / 2))
                self.window.blit(text_surface, rect)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        break

        self.send('disconnect')
        pygame.quit()


def main():
    win = pygame.display.set_mode((1512, 770))  # Set the screen to the size of the background image
    pygame.display.set_caption('Math Competition!')  # Set the title of the screen
    client = Client(win)  # Create a new client
    client.run()  # Start the game


if __name__ == '__main__':
    main()  # Start
