import random
import time
import threading
from multiplayer.util import log


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Game:
    def __init__(self, timer, largest_number=10):
        self.players = []
        self.score = {}
        self.streak = {}
        self.ready = False
        self.question = ''
        self.answers = {}
        self.duration = timer
        self.time_left = timer
        self.largest_number = largest_number
        self.timer(timer)

    @threaded
    def timer(self, s):
        if self.ready and not all(type(x) is str for x in self.score.values()) and self.score != {}:
            self.new_round()
            for _ in range(s):
                time.sleep(1)
                self.time_left -= 1
            self.question = ''
            self.answers = ''
            self.time_left = s
        self.timer(s)

    def new_round(self):
        self.question = '*'.join([str(i) for i in random.sample(range(self.largest_number + 1), 2)])
        correct_answer = eval(self.question)
        self.question = self.question.replace('*', '×')
        possible_range = range(correct_answer - 10 if correct_answer - 10 > 0 else 0,
                               correct_answer + 10 + 1)
        incorrect_answers = random.sample([i for i in possible_range if i != correct_answer], 3)
        answers = incorrect_answers + [correct_answer]
        self.answers = {answer: False if answer in incorrect_answers else True for answer in answers}
        log('GAME', 'New round started.')
        log('GAME', f'Current question: {self.question}')
        log('GAME', f'Answers: {self.answers}')

    def update_score(self, player, t, answer):
        answer = True if self.answers.get(answer, False) else False
        score = int(round((1 - (t / 10)) * 5))
        if answer:
            self.streak[player] += 1
        else:
            self.streak[player] = 0

        if 2 <= self.streak[player] <= 5:
            score += self.streak[player]
        elif self.streak[player] > 5:
            score += 5

        self.score[player] += score if score > 1 and answer else 1 if answer else 0

        if self.score[player] >= 100:
            self.score[player] = str(len([i for i in self.score.values() if type(i) is str]) + 1)

        log(f"[GAME] Updated {player.split(':')[0]}'s score (+{score if answer else 0} points) and streak.")

        return answer
