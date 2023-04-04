import socket
import pickle


class Network:
    def __init__(self, serverIP: str):
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ip = serverIP
        self._port = 5555
        self._addr = (self._ip, self._port)
        self._connect()

    def _connect(self):
        self._client.connect(self._addr)

    def send(self, data):
        self._client.sendall(pickle.dumps(data))

    def recv(self, buffer=1024):
        return pickle.loads(self._client.recv(buffer))

    def request(self):
        self.send("get")
        return self.recv()

    def close(self):
        self._client.close()

    @property
    def ip(self):
        return self._ip
