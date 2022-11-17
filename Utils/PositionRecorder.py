import psycopg2 as pg


class PositionRecorder:
    def __init__(self):
        self._user = "postgres"
        self._password = "1qaz2wsx"
        self._host = "localhost"
        self._port = "5432"
        self._db = "postgres"
        self._connection = pg.connect(user=self._user, password=self._password,
                                      host=self._host, port=self._port, database=self._db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.close()

    def addPosition(self, position: str, board: int, game: int):
        with self._connection.cursor() as curs:
            curs.execute("INSERT INTO positions(position, board, game) VALUES (%s, %s, %s)", (position, board, game))
        self._connection.commit()

    def updateResult(self, result: int):
        with self._connection.cursor() as curs:
            curs.execute("UPDATE positions SET result=%s WHERE result IS NULL", (result,))
        self._connection.commit()

    def deleteHalfPositionsOfGame(self, board: int, game: int):
        with self._connection.cursor() as curs:
            curs.execute("DELETE FROM positions WHERE board=%s AND game=%s", (board, game))
        self._connection.commit()

    def deleteLastPositions(self, count: int):
        with self._connection.cursor() as curs:
            for i in range(count):
                curs.execute("DELETE FROM positions WHERE id=(SELECT MAX(id) FROM positions)")
        self._connection.commit()
