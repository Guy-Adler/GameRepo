import socket
from multiplayer.util import *
import pickle

FORMAT = 'utf-8'


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
        """
        if t == 'username':
            msg = Response('username')
            msg.username = self.id
        elif t == 'get':
            msg = Response('get')
        elif t == 'post':
            msg = Response('post')
            msg.time = data["time"]
            msg.answer = data["answer"]
            msg.username = self.id
        elif t == 'disconnect':
            msg = Response('disconnect')
        else:
            msg = False

        msg = pickle.dumps(msg)
        self.client.send(msg)
        reply = self.client.recv(2048)
        reply = pickle.loads(reply)
        return reply
