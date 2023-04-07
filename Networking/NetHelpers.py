import socket
from dataclasses import dataclass, field
from ipaddress import IPv4Address, AddressValueError
from Engine.Move import Move


@dataclass
class GameParams:
    gameMode: int = field(default=0)
    playerNum: int = field(default=-1)
    difficulties: list[int] = field(default_factory=list)
    playerNames: list[str] = field(default_factory=list)


@dataclass
class GameStateUpdate:
    move: Move
    requiredPieces: list[str] = field(default_factory=list)


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except (socket.error, socket.herror):
        ip = '127.0.0.1'
    s.close()
    return ip


def checkIP(text: str):
    try:
        IPv4Address(text)
    except AddressValueError:
        return False
    return True
