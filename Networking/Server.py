import socket
import pickle
from threading import Thread, Barrier, Event
from queue import Queue
from Networking.NetHelpers import getIP, GameStateUpdate
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
        self._connections = [socket.socket() for _ in range(len(self._players))]
        self._barrier = Barrier(len(self._players))
        self._acceptionEvent = acceptionEvent
        self._gameParams = None
        self._lastState = Queue()
        self._sentMsg = [False for _ in range(len(self._players))]
        self._connected = [False for _ in range(len(self._players))]
        self._connecting = [False for _ in range(len(self._players))]
        self._choices = [-1 for _ in range(len(self._players))]
        self._tryBind()
        self._startAndJoinThreads(self._waitForConnection)
        if self._areTrue(self._connected):
            self._startAndJoinThreads(self._threadedClient)
        self._server.close()

    def _tryBind(self):
        self._server.bind(self._addr)
        self._server.listen(len(self._players))
        ConsoleLogger.waitingForConnection()

    def _startAndJoinThreads(self, target):
        threads = []
        for player in range(len(self._players)):
            threads.append(Thread(target=target, args=(player,)))
            threads[-1].start()
        for thread in threads:
            thread.join()

    def _waitForConnection(self, player: int):
        while not (self._areTrue(self._connected) and self._arePlayersReady()):
            if not self._handleMessages(player, self._getPlayerPosition):
                ConsoleLogger.lostConnection()
                if player == 0:
                    self._closeAllConnections()
                    break
                else:
                    self._closeConnection(player)
            if not (self._connected[player] or self._connecting[player]):
                if not self._tryConnect(player):
                    break

    def _handleMessages(self, player: int, uniqueMsgHandler):
        if not self._connected[player]:
            return True
        try:
            data = self._connections[player].recv(1024)
            if not data:
                return False
            msg = pickle.loads(data)
            uniqueMsgHandler(player, msg)
            if msg == "get":
                if self._sentMsg[player] or self._getLastState() is None:
                    self._connections[player].sendall(pickle.dumps(None))
                else:
                    self._connections[player].sendall(pickle.dumps(self._getLastState()))
                    self._sentMsg[player] = True
            if self._areTrue(self._sentMsg):
                self._sentMsg = [False for _ in range(len(self._players))]
                self._lastState.get()
            if msg == "quit":
                return False
        except (ConnectionResetError, ConnectionAbortedError):
            return False
        return True

    def _getPlayerPosition(self, player: int, msg):
        if isinstance(msg, int) and msg in range(-1, 4) and self._choices[player] == -1:
            self._choices[player] = msg
            self._lastState.put(self._choices)
        if msg == "params":
            self._connections[player].sendall(pickle.dumps(self._gameParams))
        if msg == "choice":
            self._connections[player].sendall(pickle.dumps(self._choices))
        if msg == "quit":
            self._choices[player] = -1
            self._lastState.put(self._choices)

    def _closeConnection(self, player: int):
        self._connected[player] = False
        self._connections[player].close()

    def _closeAllConnections(self):
        for player in range(len(self._players)):
            self._sendQuit(player)
            self._closeConnection(player)
        self._server.close()

    def _sendQuit(self, player: int):
        try:
            self._connections[player].sendall(pickle.dumps("quit"))
        except OSError:
            pass

    def _tryConnect(self, player: int):
        self._connecting[player] = True
        if player == 0:
            self._acceptionEvent.set()
        try:
            self._connections[player], addr = self._server.accept()
        except OSError:
            self._connecting[player] = False
            return False
        if player == 0:
            self._gameParams = pickle.loads(self._connections[player].recv(1024))
            self._acceptionEvent.set()
        ConsoleLogger.connectedToAddr(addr)
        self._connected[player] = True
        self._connecting[player] = False
        return True

    def _threadedClient(self, player: int):
        self._barrier.wait()
        self._connections[player].sendall(pickle.dumps("start"))
        while self._handleMessages(player, self._getGameStateUpdate):
            pass
        self._closeAllConnections()

    def _getGameStateUpdate(self, player, msg):
        if isinstance(msg, GameStateUpdate):
            self._lastState.put(msg)

    def _getLastState(self):
        try:
            return self._lastState.queue[0]
        except IndexError:
            return

    def _arePlayersReady(self):
        for val in self._choices:
            if val == -1:
                return False
        return True

    @staticmethod
    def _areTrue(lst: list):
        for val in lst:
            if not val:
                return False
        return True
