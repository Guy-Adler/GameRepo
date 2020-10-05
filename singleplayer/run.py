from singleplayer.game import Game
import random
import pygame
import pygame.freetype
import math
import logging
import time

pygame.init()

PI = math.pi


class Board:
    """
    Stores the background of the window, and all the cells of the board
    """

    def __init__(self, window, font):
        """
        :param window: pygame window
        :type window: pygame.Surface
        :param font: The font to use
        :type font: pygame.freetype.Font
        """
        self.win = window
        self.image = pygame.image.load('assets/board.png')  # Load the image
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
    def __init__(self, win, game):
        """
        The main class that runs the game.
        :param win: pygame window
        :type win: pygame.Surface
        """
        self.window = win
        self.w = 1512  # Width of the window
        self.h = 770  # Height of the window
        self.FONT = pygame.freetype.Font('assets/Assistant-Bold.ttf')  # setup the font
        self.board = Board(self.window, self.FONT)  # The main board (background image)
        self.board.create_cells()  # Create the cells in the board
        self.question = Question(self.window, self.FONT)  # The place for the questions
        self.answer = Answers(self.window, self.FONT)  # The place for the answers
        # Calculate the center of the first cell (index 0):
        x = int(self.board.cells[0].x + self.board.cells[0].width / 2)
        y = int(self.board.cells[0].y + self.board.cells[0].height / 2)
        self.r = 20  # Constant, The radius of the player
        self.player = Player(self.window, [0, 255, 255], (x, y, self.r))  # Will be filled later.
        self.time = 0  # The time (seconds) it took to answer the question; Will be changed later
        self.correct = True  # Whether the answer was correct or not; Will be changed later.
        self.darker = pygame.Surface((self.w, self.h))  # The surface used when darkening the screen.
        self.darker.set_alpha(90)
        self.won = False
        self.answered = False
        self.game = game

    def draw(self):
        """Draw the current screen"""
        self.board.draw()
        [cell.draw() for cell in self.board.cells]
        self.player.draw()
        self.question.draw()
        self.answer.draw()
        pygame.draw.circle(self.window, [0, 255, 255], (1133, 329), 38)
        pygame.display.update()

    def run(self):
        """The main loop of the game"""
        run = True
        message = ''
        while run:
            pygame.time.delay(100)
            player_score = self.game.score
            x = int(self.board.cells[player_score - 1].x + self.board.cells[player_score - 1].width / 2)
            y = int(self.board.cells[player_score - 1].y + self.board.cells[player_score - 1].height / 2)
            self.player.x = x
            self.player.y = y
            self.won = self.game.score >= 100

            if not self.won and not self.answered:
                message = ''
                if not all(str(answer) for answer in self.answer.answers) or self.game.question != self.question.question:
                    self.answer.answers = random.sample(list(self.game.answers.keys()), 4)
                self.question.question = self.game.question
                self.draw()
                pygame.draw.arc(self.window, (0, 0, 0),
                                (1133 - 38 - 10, 329 - 38 - 10, 2 * 38 + 20, 2 * 38 + 20), PI / 2,
                                ((2 * PI) / self.game.duration) * self.game.time_left + PI / 2, 10)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        break
                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()
                        self.time = self.game.duration - self.game.time_left
                        for index, rect in enumerate(self.answer.pos):
                            if rect[0] <= pos[0] <= rect[0] + rect[2] and rect[1] <= pos[1] <= rect[1] + rect[3]:
                                self.correct = self.game.update_score(self.time, self.answer.answers[index])
                                self.answered = True
                                with open('answers.txt', 'a', encoding='utf-8') as f:
                                    f.write(f'{self.game.question}: {self.answer.answers[index]} ({self.correct})\n')
            elif not self.won and self.answered:
                if self.game.question != self.question.question:
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
                text = ' שניות'[::-1] + str(self.game.time_left) + ' ' + 'בעוד '[::-1] + 'ממשיכים '[::-1]
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
                text = 'כל הכבוד, סיימת את המשחק!'[::-1]
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

        pygame.quit()


def main():
    logging.basicConfig(
        handlers=[logging.FileHandler(f'logs\\{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}.log',
                                      'w', 'utf-8')],
        level=logging.INFO,
        format='<%(asctime)s> %(message)s')
    win = pygame.display.set_mode((1512, 770))  # Set the screen to the size of the background image
    pygame.display.set_caption('Math Competition!')  # Set the title of the screen
    game = Game(20)
    client = Client(win, game)  # Create a new client
    client.run()  # Start the game


if __name__ == '__main__':
    main()
    quit()
