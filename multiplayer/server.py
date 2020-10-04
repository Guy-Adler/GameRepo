import socket
import threading
import json
import pickle
from multiplayer.util import *
import random
from multiplayer.game import Game
import time
import io
import logging

FORMAT = 'utf-8'
logging.basicConfig(handlers=[logging.FileHandler(f'logs\\{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}.log',
                                                  'w', 'utf-8')],
                    level=logging.INFO,
                    format='<%(asctime)s> %(message)s')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

players = int(input(f'<{time.strftime("%H:%M:%S", time.localtime())}> [SERVER] How many players will play'
                    f'(ONLY NUMBERS): '))

log('SERVER', 'Opening a server for {players} players...')

SERVER = '10.0.0.33'  # IPv4, get it when running "ipconfig"
PORT = 5050  # Port (just a number I selected)

server_ip = socket.gethostbyname(SERVER)
s.bind((SERVER, PORT))  # Bind the server to the port

s.listen()  # Start the server
log('SERVER', 'Listening for connections...')

usernames = set()  # Will store usernames
with open('assets/colors.json', 'r') as f:
    colors = json.load(f)  # Load the json file with all the colors

game = Game(20)


def threaded_client(conn, addr):
    """
    Communicate with a client
    :param conn: a socket object
    :type conn: socket.Socket
    :param addr: data about the connected guest
    :type addr: tuple
    """
    global usernames, game
    user_id = ''
    log('SERVER', f'Connected to {addr}')

    reply = Response('connection')
    with open('assets/Assistant-Bold.ttf', 'rb') as file:
        reply.font = io.BytesIO(file.read())

    with open('assets/board.png', 'rb') as file:
        reply.image = io.BytesIO(file.read())

    reply = pickle.dumps(reply)
    log('SERVER', 'Sending background image and font...')
    conn.sendall(reply)

    while True:
        data = conn.recv(2048)
        if not data:
            break
        reply = pickle.loads(data)
        if reply.type == 'username':
            if reply.username in usernames:
                log('USERNAME', f'Denied username {reply.username} for {addr} because it already exists.')
                reply = Response('username')
                reply.OK = False
            else:
                user_id = reply.username
                reply = Response('username')
                reply.OK = True
                reply.color = random.choice(list(colors.values()))
                usernames.add(user_id)
                user_id = f'{user_id}:{reply.color}'
                log('USERNAME', f'Accepted username {user_id.split(":")[0]} for {addr}, sent color {reply.color}.')
                game.players.append(user_id)
                game.score[user_id] = 1
                game.streak[user_id] = 0
                game.ready = True if len(game.players) > players - 1 else False
                if game.ready: log('GAME', 'Game started.')
            reply = pickle.dumps(reply)
            conn.sendall(reply)

        elif reply.type == 'get':
            reply = pickle.dumps(game)
            conn.sendall(reply)

        elif reply.type == 'post':
            log('POST', '{user_id.split(":")[0]} (client {addr}) sent a POST request: '
                        '{reply.username, reply.time, reply.answer = } Transferring the request to the game...')
            reply = game.update_score(reply.username, reply.time, reply.answer)
            reply = pickle.dumps(reply)
            conn.sendall(reply)

        elif reply.type == 'disconnect':
            reply = pickle.dumps('Goodbye')
            conn.sendall(reply)
            break

    log('DISCONNECT', f'Connection closed by {user_id.split(":")[0]} (client {addr}).')
    del game.score[user_id]
    del game.streak[user_id]
    game.players.remove(user_id)
    usernames.remove(user_id.split(':')[0])

    conn.close()


if __name__ == '__main__':
    while True:
        connection, address = s.accept()  # Accept a connection.
        threading.Thread(target=threaded_client, args=(connection, address)).start()
