import socket
import pickle
from copy import deepcopy
from threading import Thread, Barrier, Event, Lock
from queue import Queue
from Engine.Move import Move
from Networking.NetHelpers import getIP
from Utils.Logger import ConsoleLogger


class Server:
    def __init__(self, freePlayers: list[int], acceptionEvent: Event):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ip = getIP()
        self._port = 5555
        self._addr = (self._ip, self._port)
        if len(freePlayers) == 0:
            self._players = [0]
        else:
            self._players = freePlayers
        self._connections: {int: socket.socket} = {}
        self._barrier = Barrier(len(self._players))
        self._lock = Lock()
        self._acceptionEvent = acceptionEvent
        self._gameParams = {}
        self._lastMove = Queue()
        self._sentMove = {player: False for player in self._players}
        self._tryBind()
        self._waitForConnections()

    def _tryBind(self):
        self._server.bind(self._addr)
        self._server.listen(len(self._players))
        ConsoleLogger.waitingForConnection()

    def _waitForConnections(self):
        threads = []
        for i, player in enumerate(self._players):
            if i == 0:
                self._acceptionEvent.set()
            conn, addr = self._server.accept()
            if i == 0:
                self._gameParams = pickle.loads(conn.recv(1024))
            self._connections[player] = conn
            ConsoleLogger.connectedToAddr(addr, player + 1)
            threads.append(Thread(target=self._threadedClient, args=(conn, player)))
            threads[-1].start()
        for thread in threads:
            thread.join()
        self._server.close()

    def _threadedClient(self, conn: socket.socket, player: int):
        self._barrier.wait()
        gameParams = deepcopy(self._gameParams)
        gameParams["playerNum"] = player
        conn.sendall(pickle.dumps(gameParams))
        working = True
        while working:
            working = self._retransmitData(player)
        ConsoleLogger.lostConnection()
        for i, connection in self._connections.items():
            if i == player:
                continue
            connection.sendall(pickle.dumps("quit"))
        conn.close()

    def _retransmitData(self, player: int):
        data = self._connections[player].recv(1024)
        if not data:
            return False
        msg = pickle.loads(data)
        if isinstance(msg, Move):
            self._lastMove.put(msg)
        if msg == "get":
            if self._sentMove[player] or self._getLastMove() is None:
                self._connections[player].sendall(pickle.dumps(None))
            else:
                self._connections[player].sendall(pickle.dumps(self._getLastMove()))
                self._sentMove[player] = True
        if self._sentToAll():
            self._sentMove = {player: False for player in self._players}
            self._lastMove.get()
        if msg == "quit":
            return False
        return True

    def _getLastMove(self):
        try:
            return self._lastMove.queue[0]
        except IndexError:
            return

    def _sentToAll(self):
        for val in self._sentMove.values():
            if not val:
                return False
        return True

    @property
    def ip(self):
        return self._ip
