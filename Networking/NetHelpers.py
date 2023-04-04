from ipaddress import IPv4Address, AddressValueError
import socket


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


def handleSocketError(func):
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except socket.error as e:
            print(e)
        return result
    return wrapper


def checkIP(text: str):
    try:
        IPv4Address(text)
    except AddressValueError:
        return False
    return True
