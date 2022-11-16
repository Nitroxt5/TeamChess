#include <Python.h>
#define ULL unsigned long long
#define PY_SSIZE_T_CLEAN

long weights[] = {15,  // for positioning the rook on the semi-open file with pawn of the same color
                  20,  // for positioning the rook on the semi-open file with pawn of the opposite color
                  30,  // for positioning the rook on the open file
                  20,  // for positioning the rook on the penultimate row
                  3,   // for every possible (not necessary valid) knight move
                  4,   // for every possible (not necessary valid) bishop move
                  50,  // for castling
                  20,  // for checking opponent king
                  70,  // for castling deprivation (for each side)
                  30,  // for pawn shield in front of king
                  10,  // for pseudo passed pawn
                  20,  // penalty for doubled pawns
                  30,  // penalty for tripled pawns
                  20,  // penalty for early queen participation
                  30}; // for center control (for each square)

long knightPositionScore[8][8] = { 1, 2, 1, 1, 1, 1, 2, 1,
								   1, 2, 2, 2, 2, 2, 2, 1,
								   1, 2, 3, 3, 3, 3, 2, 1,
								   1, 2, 3, 4, 4, 3, 2, 1,
								   1, 2, 3, 4, 4, 3, 2, 1,
								   1, 2, 3, 3, 3, 3, 2, 1,
								   1, 2, 2, 2, 2, 2, 2, 1,
								   1, 2, 1, 1, 1, 1, 2, 1 };

long bishopPositionScore[8][8] = { 3, 2, 2, 1, 1, 2, 2, 3,
								   2, 4, 3, 3, 3, 3, 4, 2,
								   2, 3, 3, 3, 3, 3, 3, 2,
								   2, 3, 3, 3, 3, 3, 3, 2,
								   2, 3, 3, 3, 3, 3, 3, 2,
								   2, 3, 3, 3, 3, 3, 3, 2,
								   2, 4, 3, 3, 3, 3, 4, 2,
								   3, 2, 2, 1, 1, 2, 2, 3 };

long queenPositionScore[8][8] = { 1, 1, 1, 2, 1, 1, 1, 1,
								  1, 1, 2, 2, 1, 1, 1, 1,
								  1, 2, 1, 2, 1, 1, 1, 1,
								  1, 1, 1, 2, 1, 1, 1, 1,
								  1, 1, 1, 2, 1, 1, 1, 1,
								  1, 2, 1, 2, 1, 1, 1, 1,
								  1, 1, 2, 2, 1, 1, 1, 1,
								  1, 1, 1, 2, 1, 1, 1, 1 };

long rookPositionScore[8][8] = { 3, 3, 3, 3, 3, 3, 3, 3,
								 2, 2, 2, 2, 2, 2, 2, 2,
								 2, 2, 2, 2, 2, 2, 2, 2,
								 1, 2, 2, 2, 2, 2, 2, 1,
								 1, 2, 2, 2, 2, 2, 2, 1,
								 2, 2, 2, 2, 2, 2, 2, 2,
								 2, 2, 2, 2, 2, 2, 2, 2,
								 3, 3, 3, 3, 3, 3, 3, 3 };

long whitePawnPositionScore[8][8] = { 6, 6, 6, 6, 6, 6, 6, 6,
									  5, 5, 5, 5, 5, 5, 5, 5,
									  4, 4, 4, 4, 4, 4, 4, 4,
									  3, 3, 3, 4, 4, 3, 3, 3,
									  1, 2, 2, 4, 4, 2, 2, 1,
									  2, 1, 2, 3, 3, 1, 1, 2,
									  1, 1, 1, 0, 0, 1, 1, 1,
									  0, 0, 0, 0, 0, 0, 0, 0 };

long blackPawnPositionScore[8][8] = { 0, 0, 0, 0, 0, 0, 0, 0,
									  1, 1, 1, 0, 0, 1, 1, 1,
									  2, 1, 2, 3, 3, 1, 1, 2,
									  1, 2, 2, 4, 4, 2, 2, 1,
									  3, 3, 3, 4, 4, 3, 3, 3,
									  4, 4, 4, 4, 4, 4, 4, 4,
									  5, 5, 5, 5, 5, 5, 5, 5,
									  6, 6, 6, 6, 6, 6, 6, 6 };

//[0..7] = [a..h]

ULL bbOfColumns[8] = { 0b1000000010000000100000001000000010000000100000001000000010000000,
					   0b0100000001000000010000000100000001000000010000000100000001000000,
					   0b0010000000100000001000000010000000100000001000000010000000100000,
					   0b0001000000010000000100000001000000010000000100000001000000010000,
					   0b0000100000001000000010000000100000001000000010000000100000001000,
					   0b0000010000000100000001000000010000000100000001000000010000000100,
					   0b0000001000000010000000100000001000000010000000100000001000000010,
					   0b0000000100000001000000010000000100000001000000010000000100000001 };

//[0..7] = [8..1]

ULL bbOfRows[8] = { 0b1111111100000000000000000000000000000000000000000000000000000000,
					0b0000000011111111000000000000000000000000000000000000000000000000,
					0b0000000000000000111111110000000000000000000000000000000000000000,
					0b0000000000000000000000001111111100000000000000000000000000000000,
					0b0000000000000000000000000000000011111111000000000000000000000000,
					0b0000000000000000000000000000000000000000111111110000000000000000,
					0b0000000000000000000000000000000000000000000000001111111100000000,
					0b0000000000000000000000000000000000000000000000000000000011111111 };

ULL bbOfCenter = 0b0000000000000000000000000001100000011000000000000000000000000000;

//[0..7] = [a, ab, h, gh, 1, 12, 8, 78]

ULL bbOfCorrections[8] = { 0b0111111101111111011111110111111101111111011111110111111101111111,
						   0b0011111100111111001111110011111100111111001111110011111100111111,
						   0b1111111011111110111111101111111011111110111111101111111011111110,
						   0b1111110011111100111111001111110011111100111111001111110011111100,
						   0b1111111111111111111111111111111111111111111111111111111100000000,
						   0b1111111111111111111111111111111111111111111111110000000000000000,
						   0b0000000011111111111111111111111111111111111111111111111111111111,
						   0b0000000000000000111111111111111111111111111111111111111111111111 };

long CASTLE_SIDES[4] = { 8, 4, 2, 1 };

long queenScore = 1200;
long rookScore = 600;
long bishopScore = 400;
long knightScore = 400;
long pawnScore = 100;

struct MyArr
{
	ULL arr[16] = { 0 };
	int size = 0;

	void append(ULL item)
	{
		arr[size] = item;
		++size;
	}
};

MyArr numSplit(ULL number)
{
	MyArr result;
	while (number)
	{
		ULL tmp = number & (0 - number);
		result.append(tmp);
		number -= tmp;
	}
	return result;
}

long getPower(ULL number)
{
	long counter = 0;
	while (number)
	{
		number >>= 1;
		++counter;
	}
	return 64 - counter;
}

long getBitsCount(ULL number)
{
	long counter = 0;
	while (number)
	{
		if (number & 1)
		{
			++counter;
		}
		number >>= 1;
	}
	return counter;
}

bool getCastleRight(long currentCastlingRight, long right)
{
	return (currentCastlingRight & right) != 0;
}

long scoreRookPositioning(ULL whitebbOfRooks, ULL blackbbOfRooks, ULL whitebbOfPawns, ULL blackbbOfPawns, long whiteRookReserveCount, long blackRookReserveCount)
{
	long score = 0;
	for (int i = 0; i < 8;i++)
	{
		ULL whiteRookPos = bbOfColumns[i] & whitebbOfRooks;
		ULL	blackRookPos = bbOfColumns[i] & blackbbOfRooks;
		if (whiteRookPos | blackRookPos)
		{
			ULL whitePawnsPos = bbOfColumns[i] & whitebbOfPawns;
			ULL	blackPawnsPos = bbOfColumns[i] & blackbbOfPawns;
			long whitePawnsCount = getBitsCount(whitePawnsPos);
			long blackPawnsCount = getBitsCount(blackPawnsPos);
			if (whiteRookPos)
			{
				if (blackPawnsCount == 0 && whitePawnsCount == 1)
				{
					score += weights[0];
				}
				else if (whitePawnsCount == 0 && blackPawnsCount >= 1)
				{
					score += weights[1];
				}
				else if (whitePawnsCount + blackPawnsCount == 0)
				{
					score += weights[2];
				}
			}
			if (blackRookPos)
			{
				if (whitePawnsCount == 0 && blackPawnsCount == 1)
				{
					score -= weights[0];
				}
				else if (blackPawnsCount == 0 && whitePawnsCount >= 1)
				{
					score -= weights[1];
				}
				else if (whitePawnsCount + blackPawnsCount == 0)
				{
					score -= weights[2];
				}
			}
		}
	}
	ULL whiteRookRowPos = bbOfRows[1] & whitebbOfRooks;
	ULL blackRookRowPos = bbOfRows[6] & blackbbOfRooks;
	if (blackRookRowPos)
	{
		score -= getBitsCount(blackRookRowPos) * weights[3];
	}
	if (whiteRookRowPos)
	{
		score += getBitsCount(whiteRookRowPos) * weights[3];
	}
	MyArr whiteSplitPositions = numSplit(whitebbOfRooks);
	MyArr blackSplitPositions = numSplit(blackbbOfRooks);
	score += (whiteSplitPositions.size - blackSplitPositions.size) * rookScore;
	score += (long)((whiteRookReserveCount - blackRookReserveCount) * rookScore * 0.8);
	for (int i = 0;i < whiteSplitPositions.size; i++)
	{
		long pos = getPower(whiteSplitPositions.arr[i]);
		score += rookPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	for (int i = 0;i < blackSplitPositions.size; i++)
	{
		long pos = getPower(blackSplitPositions.arr[i]);
		score -= rookPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	return score;
}

long scoreKnightPositioning(ULL whitebbOfKnights, ULL blackbbOfKnights, long whiteKnightReserveCount, long blackKnightReserveCount)
{
	ULL knightMoves[2] = { 0 };
	for (int i = 0;i < 2;i++)
	{
		ULL bb = i == 0 ? whitebbOfKnights : blackbbOfKnights;
		knightMoves[i] |= ((bb & bbOfCorrections[2] & bbOfCorrections[7]) << 15);
		knightMoves[i] |= ((bb & bbOfCorrections[3] & bbOfCorrections[6]) << 6);
		knightMoves[i] |= ((bb & bbOfCorrections[3] & bbOfCorrections[4]) >> 10);
		knightMoves[i] |= ((bb & bbOfCorrections[2] & bbOfCorrections[5]) >> 17);
		knightMoves[i] |= ((bb & bbOfCorrections[0] & bbOfCorrections[5]) >> 15);
		knightMoves[i] |= ((bb & bbOfCorrections[1] & bbOfCorrections[4]) >> 6);
		knightMoves[i] |= ((bb & bbOfCorrections[1] & bbOfCorrections[6]) << 10);
		knightMoves[i] |= ((bb & bbOfCorrections[0] & bbOfCorrections[7]) << 17);
	}
	long score = (getBitsCount(knightMoves[0]) - getBitsCount(knightMoves[1])) * weights[4];
	MyArr whiteSplitPositions = numSplit(whitebbOfKnights);
	MyArr blackSplitPositions = numSplit(blackbbOfKnights);
	score += (whiteSplitPositions.size - blackSplitPositions.size) * knightScore;
	score += (long)((whiteKnightReserveCount - blackKnightReserveCount) * knightScore * 0.8);
	for (int i = 0;i < whiteSplitPositions.size; i++)
	{
		long pos = getPower(whiteSplitPositions.arr[i]);
		score += knightPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	for (int i = 0;i < blackSplitPositions.size; i++)
	{
		long pos = getPower(blackSplitPositions.arr[i]);
		score -= knightPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	return score;
}

long scoreBishopPositioning(ULL whitebbOfBishops, ULL blackbbOfBishops, ULL whitebbOfPawns, ULL blackbbOfPawns, long whiteBishopReserveCount, long blackBishopReserveCount)
{
	long score = 0;
	ULL checkingSq;
	for (int i = 0;i < 2;i++)
	{
		long diffCount = i == 0 ? 1 : -1;
		ULL bb = i == 0 ? whitebbOfBishops : blackbbOfBishops;
		ULL allyPawns = i == 0 ? whitebbOfPawns : blackbbOfPawns;
		ULL enemyPawns = i == 1 ? whitebbOfPawns : blackbbOfPawns;
		MyArr splitPositions = numSplit(bb);
		for (int j = 0; j < splitPositions.size;j++)
		{
			checkingSq = splitPositions.arr[j];
			while (checkingSq & bbOfCorrections[2] & bbOfCorrections[6])
			{
				checkingSq <<= 7;
				if (checkingSq & allyPawns)
				{
					break;
				}
				if (checkingSq & enemyPawns)
				{
					score += diffCount;
					break;
				}
				score += diffCount;
			}
			checkingSq = splitPositions.arr[j];
			while (checkingSq & bbOfCorrections[2] & bbOfCorrections[4])
			{
				checkingSq >>= 9;
				if (checkingSq & allyPawns)
				{
					break;
				}
				if (checkingSq & enemyPawns)
				{
					score += diffCount;
					break;
				}
				score += diffCount;
			}
			checkingSq = splitPositions.arr[j];
			while (checkingSq & bbOfCorrections[0] & bbOfCorrections[4])
			{
				checkingSq >>= 7;
				if (checkingSq & allyPawns)
				{
					break;
				}
				if (checkingSq & enemyPawns)
				{
					score += diffCount;
					break;
				}
				score += diffCount;
			}
			checkingSq = splitPositions.arr[j];
			while (checkingSq & bbOfCorrections[0] & bbOfCorrections[6])
			{
				checkingSq <<= 9;
				if (checkingSq & allyPawns)
				{
					break;
				}
				if (checkingSq & enemyPawns)
				{
					score += diffCount;
					break;
				}
				score += diffCount;
			}
		}
	}
	MyArr whiteSplitPositions = numSplit(whitebbOfBishops);
	MyArr blackSplitPositions = numSplit(blackbbOfBishops);
	score *= weights[5];
	score += (whiteSplitPositions.size - blackSplitPositions.size) * bishopScore;
	score += (long)((whiteBishopReserveCount - blackBishopReserveCount) * bishopScore * 0.8);
	for (int i = 0;i < whiteSplitPositions.size; i++)
	{
		long pos = getPower(whiteSplitPositions.arr[i]);
		score += bishopPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	for (int i = 0;i < blackSplitPositions.size; i++)
	{
		long pos = getPower(blackSplitPositions.arr[i]);
		score -= bishopPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	return score;
}

long scoreKingSafety(ULL whitebbOfKing, ULL blackbbOfKing, ULL whitebbOfPawns, ULL blackbbOfPawns, bool isWhiteCastled, bool isBlackCastled, bool isWhiteInCheck, bool isBlackInCheck, long currentCastlingRight)
{
	long score = 0;
	if (isWhiteCastled)
	{
		score += weights[6];
	}
	if (isBlackCastled)
	{
		score -= weights[6];
	}
	if (isWhiteInCheck)
	{
		score -= weights[7];
	}
	if (isBlackInCheck)
	{
		score += weights[7];
	}
	for (int i = 0;i < 4;i++)
	{
		if (!getCastleRight(currentCastlingRight, CASTLE_SIDES[i]))
		{
			if ((i == 0 || i == 1) && !isWhiteCastled)
			{
				score -= weights[8];
			}
			else if ((i == 2 || i == 3) && !isBlackCastled)
			{
				score += weights[8];
			}
		}
	}
	for (int i = 0; i < 8;i++)
	{
		ULL whiteKingPos = bbOfColumns[i] & whitebbOfKing;
		ULL	blackKingPos = bbOfColumns[i] & blackbbOfKing;
		if (whiteKingPos)
		{
			ULL whitePawnsPos = bbOfColumns[i] & whitebbOfPawns;
			long whitePawnsCount = getBitsCount(whitePawnsPos);
			if (whitePawnsCount == 0)
			{
				score -= weights[9];
			}
		}
		if (blackKingPos)
		{
			ULL blackPawnsPos = bbOfColumns[i] & blackbbOfPawns;
			long blackPawnsCount = getBitsCount(blackPawnsPos);
			if (blackPawnsCount == 0)
			{
				score += weights[9];
			}
		}
	}
	return score;
}

long scorePawnPositioning(ULL whitebbOfPawns, ULL blackbbOfPawns, long whitePawnReserveCount, long blackPawnReserveCount)
{
	long score = 0;
	for (int i = 0; i < 8; i++)
	{
		ULL whitePawnsColumn = bbOfColumns[i] & whitebbOfPawns;
		ULL	blackPawnsColumn = bbOfColumns[i] & blackbbOfPawns;
		if ((whitePawnsColumn | blackPawnsColumn) - whitePawnsColumn == 0)
		{
			score += weights[10];
		}
		if ((whitePawnsColumn | blackPawnsColumn) - blackPawnsColumn == 0)
		{
			score -= weights[10];
		}
		long whitePawnsCount = getBitsCount(whitePawnsColumn);
		long blackPawnsCount = getBitsCount(blackPawnsColumn);
		if (whitePawnsCount == 2)
		{
			score -= weights[11];
		}
		if (whitePawnsCount >= 3)
		{
			score -= weights[12];
		}
		if (blackPawnsCount == 2)
		{
			score += weights[11];
		}
		if (blackPawnsCount >= 3)
		{
			score += weights[12];
		}
	}
	MyArr whiteSplitPositions = numSplit(whitebbOfPawns);
	MyArr blackSplitPositions = numSplit(blackbbOfPawns);
	score += (whiteSplitPositions.size - blackSplitPositions.size) * pawnScore;
	score += (long)((whitePawnReserveCount - blackPawnReserveCount) * pawnScore * 0.8);
	for (int i = 0;i < whiteSplitPositions.size; i++)
	{
		long pos = getPower(whiteSplitPositions.arr[i]);
		score += whitePawnPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	for (int i = 0;i < blackSplitPositions.size; i++)
	{
		long pos = getPower(blackSplitPositions.arr[i]);
		score -= blackPawnPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	return score;
}

long scoreQueenPositioning(ULL whitebbOfQueens, ULL blackbbOfQueens, long whiteQueenReserveCount, long blackQueenReserveCount, long gameLogLen, const char lastPieceMoved, int turn)
{
	long score = 0;
	if (gameLogLen != 0)
	{
		if (gameLogLen < 20 && lastPieceMoved == 'Q')
		{
			if (turn)
			{
				score += weights[13];
			}
			else
			{
				score -= weights[13];
			}
		}
	}
	MyArr whiteSplitPositions = numSplit(whitebbOfQueens);
	MyArr blackSplitPositions = numSplit(blackbbOfQueens);
	score += (whiteSplitPositions.size - blackSplitPositions.size) * queenScore;
	score += (long)((whiteQueenReserveCount - blackQueenReserveCount) * queenScore * 0.8);
	for (int i = 0;i < whiteSplitPositions.size; i++)
	{
		long pos = getPower(whiteSplitPositions.arr[i]);
		score += queenPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	for (int i = 0;i < blackSplitPositions.size; i++)
	{
		long pos = getPower(blackSplitPositions.arr[i]);
		score -= queenPositionScore[(long)(pos / 8)][pos % 8] * 10;
	}
	return score;
}

long scoreCenterControl(ULL whitebbOfOccupiedSq, ULL blackbbOfOccupiedSq)
{
	ULL whiteCenterControl = bbOfCenter & whitebbOfOccupiedSq;
	ULL blackCenterControl = bbOfCenter & blackbbOfOccupiedSq;
	return (getBitsCount(whiteCenterControl) - getBitsCount(blackCenterControl)) * weights[14];
}

static PyObject* scoreBoard(PyObject* self, PyObject* gs)
{
	PyObject* checkmate = PyObject_GetAttrString(gs, "checkmate");
	PyObject* stalemate = PyObject_GetAttrString(gs, "stalemate");
	PyObject* whiteTurn = PyObject_GetAttrString(gs, "whiteTurn");

	int cm = PyObject_IsTrue(checkmate);
	int sm = PyObject_IsTrue(stalemate);
	int turn = PyObject_IsTrue(whiteTurn);

	if (cm)
	{
		if (turn)
		{
			return PyLong_FromLong(-100000);
		}
		else
		{
			return PyLong_FromLong(100000);
		}
	}
	else if (sm)
	{
		return PyLong_FromLong(0);
	}

	PyObject* bbOfPiecesPy = PyObject_GetAttrString(gs, "bbOfPieces");
	PyObject* bbOfOccupiedSqPy = PyObject_GetAttrString(gs, "bbOfOccupiedSquares");
	PyObject* reservePy = PyObject_GetAttrString(gs, "reserve");
	PyObject* whiteInCheck = PyObject_GetAttrString(gs, "isWhiteInCheck");
	PyObject* blackInCheck = PyObject_GetAttrString(gs, "isBlackInCheck");
	PyObject* whiteCastled = PyObject_GetAttrString(gs, "isWhiteCastled");
	PyObject* blackCastled = PyObject_GetAttrString(gs, "isBlackCastled");
	PyObject* currentCastlingRightPy = PyObject_GetAttrString(gs, "currentCastlingRight");
	PyObject* currentValidMovesCountPy = PyObject_GetAttrString(gs, "currentValidMovesCount");
	PyObject* lastPieceMovedPy = PyObject_GetAttrString(gs, "lastPieceMoved");
	PyObject* gameLogLenPy = PyObject_GetAttrString(gs, "gameLogLen");

	const char pieces[12][3] = { "wK", "wQ", "wR", "wB", "wN", "wp", "bK", "bQ", "bR", "bB", "bN", "bp" };
	ULL bbOfPieces[12] = { 0 };

	for (int i = 0;i < 12;i++)
	{
		PyObject* tmpObj = PyDict_GetItemString(bbOfPiecesPy, pieces[i]);
		bbOfPieces[i] = PyLong_AsUnsignedLongLong(tmpObj);
	}

	const char occupationTypes[3][2] = { "w", "b", "a" };
	ULL bbOfOccupiedSquares[3] = { 0 };

	for (int i = 0;i < 3;i++)
	{
		PyObject* tmpObj = PyDict_GetItemString(bbOfOccupiedSqPy, occupationTypes[i]);
		bbOfOccupiedSquares[i] = PyLong_AsUnsignedLongLong(tmpObj);
	}

	PyObject* whiteReservePy = PyDict_GetItemString(reservePy, "w");
	PyObject* blackReservePy = PyDict_GetItemString(reservePy, "b");
	const char reservePieces[5][2] = { "Q", "R", "B", "N", "p" };
	long whiteReserve[5] = { 0 };
	long blackReserve[5] = { 0 };

	for (int i = 0;i < 5;i++)
	{
		PyObject* tmpObj1 = PyDict_GetItemString(whiteReservePy, reservePieces[i]);
		PyObject* tmpObj2 = PyDict_GetItemString(blackReservePy, reservePieces[i]);
		whiteReserve[i] = PyLong_AsLong(tmpObj1);
		blackReserve[i] = PyLong_AsLong(tmpObj2);
	}

	int isWhiteCastled = PyObject_IsTrue(whiteCastled);
	int isBlackCastled = PyObject_IsTrue(blackCastled);
	int isWhiteInCheck = PyObject_IsTrue(whiteInCheck);
	int isBlackInCheck = PyObject_IsTrue(blackInCheck);

	long currentCastlingRight = PyLong_AsLong(currentCastlingRightPy);

	long currentValidMovesCount = PyLong_AsLong(currentValidMovesCountPy);

	long gameLogLen = PyLong_AsLong(gameLogLenPy);
	char* lastPieceMoved;
    PyArg_Parse(lastPieceMovedPy, "s", &lastPieceMoved);
    char LPM = lastPieceMoved[0];

	long score = 0;

	if (turn)
	{
		score += currentValidMovesCount;
	}
	else
	{
		score -= currentValidMovesCount;
	}

	score += scoreRookPositioning(bbOfPieces[2], bbOfPieces[8], bbOfPieces[5], bbOfPieces[11], whiteReserve[1], blackReserve[1]);
	score += scoreKnightPositioning(bbOfPieces[4], bbOfPieces[10], whiteReserve[3], blackReserve[3]);
	score += scoreBishopPositioning(bbOfPieces[3], bbOfPieces[9], bbOfPieces[5], bbOfPieces[11], whiteReserve[2], blackReserve[2]);
	score += scoreKingSafety(bbOfPieces[0], bbOfPieces[6], bbOfPieces[5], bbOfPieces[11], isWhiteCastled, isBlackCastled, isWhiteInCheck, isBlackInCheck, currentCastlingRight);
	score += scorePawnPositioning(bbOfPieces[5], bbOfPieces[11], whiteReserve[4], blackReserve[4]);
	score += scoreQueenPositioning(bbOfPieces[1], bbOfPieces[7], whiteReserve[0], blackReserve[0], gameLogLen, LPM, turn);
	score += scoreCenterControl(bbOfOccupiedSquares[0], bbOfOccupiedSquares[1]);

	return PyLong_FromLong(score);
}

static PyMethodDef ScoreBoard_methods[] = {
	{ "scoreBoard", (PyCFunction)scoreBoard, METH_O, ""},
	{ NULL, NULL, 0, NULL }
};

static PyModuleDef ScoreBoard_module = {
	PyModuleDef_HEAD_INIT,
	"ScoreBoard",
	"Provides a fast score board function",
	-1,
	ScoreBoard_methods
};

PyMODINIT_FUNC PyInit_ScoreBoard() {
	return PyModule_Create(&ScoreBoard_module);
}