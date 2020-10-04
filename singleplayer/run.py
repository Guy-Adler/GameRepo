from game import Game
import random
import time


def main(game, username):
    while True:
        response = game.new_round(10)
        print(response['question'] + '?')
        answers = random.sample(list(response['answers'].keys()), len(list(response['answers'].keys())))
        possible_answers = []
        alpha = {
            0: 'a',
            1: 'b',
            2: 'c',
            3: 'd'
        }
        for index, key in enumerate(answers):
            possible_answers.append(f'{alpha[index]}: {key}')

        print('    '.join(possible_answers))
        start = time.time()
        answer = input('> ')
        end = time.time()
        if answer in 'abcd' and len(answer) == 1:
            answer = answers[list(alpha.keys())[list(alpha.values()).index(answer)]]
            answer = response['answers'][answer]
            print(f'You were {"correct!" if answer else "incorrect!"}')
            game.update_score({'username': username, 'time': end - start, 'answer': answer})
            print(f'You have {game.scoreboard[username]} points!')
            print('Getting a new question...')
            time.sleep(2)
        else:
            print('Invalid answer. The answer will not count towards the scoreboard.')
            print('Getting a new question...')
            time.sleep(2)


if __name__ == '__main__':
    user = input('Choose your username: ')
    session = Game([user])
    while True:
        main(session, user)
