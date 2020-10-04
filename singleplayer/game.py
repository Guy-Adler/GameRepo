import random


class Game:
    def __init__(self, players):
        """
        :param players: All player's usernames.
        :type players: list
        """
        self.players = players
        self.scoreboard = {player: 0 for player in players}
        self.streak = {player: 0 for player in players}

    @staticmethod
    def new_round(largest_number):
        """
        Create a new round of the game.
        :param largest_number: Largest number to be multiplied.
        :return: Dictionary question and answers, the keys being True or False.
        :rtype: Dict
        """
        question = '*'.join([str(i) for i in random.sample(range(largest_number + 1), 2)])
        correct_answer = eval(question)
        possible_range = [i for i in range(correct_answer - 10, correct_answer + 10 + 1)]
        incorrect_answers = []
        while len(incorrect_answers) < 3:
            answer = random.choice([i for i in possible_range])
            if answer != correct_answer and answer not in [-1 * i if i < 0 else i for i in incorrect_answers]:
                incorrect_answers.append(-1 * answer if answer < 0 else answer)
        answers = incorrect_answers + [correct_answer]
        answers = {answer: False if answer in incorrect_answers else True for answer in answers}
        response = {
            'question': question,
            'answers': answers
        }
        return response

    def update_score(self, response):
        """
        Update the scoreboard based on the way Kahoot scores.
        :param response: A dict including the time it took the player to answer and the answer chosen.
        :type response: dict
        """
        username = response['username']
        score = int(round((1 - (response['time'] / 10)) * 10))
        if response['answer']:
            self.streak[username] += 1
        else:
            self.streak[username] = 0

        if 2 <= self.streak[username] <= 5:
            score += self.streak[username]
        elif self.streak[username] > 5:
            score += 5

        self.scoreboard[username] += score
