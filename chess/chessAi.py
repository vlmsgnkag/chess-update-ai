'''
    Keep DEPTH <= 4 for AI to run smoothly.

    DEPTH means the fot will looks depth moves ahead and calculate the best possible move based on PIECE-CAPTURE-SCORE AND PIECE-POSITION SCORE :
    DEPTH = 4
'''


'''

WAYS TO IMPROVE AI AND MAKE AI FASTER

1) Create a database for initial ai moves/ book openings
2) AI find possible moves for all the piece after each move, if one piece is moved possible moves for other piece would be same no need to find again
    In this case new possible move would be :
        i) if any piece could move to the starting location of piece moved
        ii) if the piece moved to (x, y) position check if it blocked any piece to move to that location
3) no need to evaluate all the position again and again use zobrus hashing to save good position and depth
4) if [ black moved x, white move a, black moved y, white move b ] is sometime same as: 
      [ black moved y, white move a, black moved x, white move b ]
      [ black moved x, white move b, black moved y, white move a ]
      [ black moved y, white move b, black moved y, white move a ]
5) Teach theories to AI, like some time it is better to capture threat than to move a pawn or take back our piece to previous position rather than attacking


'''
import os
import json
import random
BOOK_FILE = "book_openings.json"
try:
    with open(BOOK_FILE, "r") as f:
        BOOK = json.load(f)
except:
    BOOK = []

def learnOpeningFromWin(moveLog):
    opening = [str(m) for m in moveLog[:5]]
    if opening not in BOOK:
        BOOK.append(opening)
        with open(BOOK_FILE, "w") as f:
            json.dump(BOOK, f, indent=2)
            
Q_FILE = "q_table.json"
if os.path.exists(Q_FILE):
    with open(Q_FILE, "r") as f:
        Q_TABLE = json.load(f)
else:
    Q_TABLE = {}

def updateQLearning(moveLog, result):
    for move in moveLog:
        if move not in Q_TABLE:
            Q_TABLE[move] = 0
        Q_TABLE[move] += 1 if result == "win" else -1

    with open(Q_FILE, "w") as f:
        json.dump(Q_TABLE, f, indent=2)
ZOBRIST_TABLE = [[[random.getrandbits(64) for _ in range(12)] for _ in range(8)] for _ in range(8)]
ZOBRIST_TURN = random.getrandbits(64)
PIECE_TO_INDEX = {
    'wK': 0, 'wQ': 1, 'wR': 2, 'wB': 3, 'wN': 4, 'wp': 5,
    'bK': 6, 'bQ': 7, 'bR': 8, 'bB': 9, 'bN': 10, 'bp': 11
}
def zobristHash(gs):
    h = 0
    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece != '--':
                pieceIndex = PIECE_TO_INDEX[piece]
                h ^= ZOBRIST_TABLE[r][c][pieceIndex]
    if gs.whiteToMove:
        h ^= ZOBRIST_TURN
    return h
pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 2, 1, 1, 2, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]


piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores,
                       "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}


CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
SET_WHITE_AS_BOT = -1


def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves, returnQueue):
    global nextMove, whitePawnScores, blackPawnScores
    nextMove = None
    random.shuffle(validMoves)

    if gs.playerWantsToPlayAsBlack:
        # Swap the variables
        whitePawnScores, blackPawnScores = blackPawnScores, whitePawnScores

    SET_WHITE_AS_BOT = 1 if gs.whiteToMove else -1

    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -
                             CHECKMATE, CHECKMATE,  SET_WHITE_AS_BOT)

    returnQueue.put(nextMove)


# with alpha beta pruning
'''
alpha is keeping track of maximum so far
beta is keeping track of minimum so far
'''


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, TT_CACHE
    zobrist = zobristHash(gs)

    if zobrist in TT_CACHE and TT_CACHE[zobrist]['depth'] >= depth:
        return TT_CACHE[zobrist]['score']

    if depth == 0:
        score = turnMultiplier * scoreBoard(gs)
        TT_CACHE[zobrist] = {'score': score, 'depth': depth}
        return score

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    TT_CACHE[zobrist] = {'score': maxScore, 'depth': depth}
    return maxScore
'''
Positive score is good for white
Negative score is good for black
'''


def scoreBoard(gs):
    if gs.checkmate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    pieceCount = 0
    for r in range(8):
        for c in range(8):
            square = gs.board[r][c]
            if square != "--":
                pieceType = square[1]
                pieceColor = 1 if square[0] == 'w' else -1
                pieceValue = pieceScore.get(pieceType, 0)
                posValue = 0

                # Tính điểm vị trí
                if pieceType == "p":
                    key = square
                    if key in piecePositionScores:
                        posValue = piecePositionScores[key][r][c]
                elif pieceType in piecePositionScores:
                    posValue = piecePositionScores[pieceType][r][c]

                score += pieceColor * (pieceValue + posValue * 0.1)
                pieceCount += 1

                # Trung tâm (d4, e4, d5, e5)
                if (r, c) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    score += 0.2 * pieceColor

    # Endgame: ít quân → vua nên hoạt động nhiều hơn
    if pieceCount < 10:
        score += kingActivityScore(gs)

    return score

def kingActivityScore(gs):
    score = 0
    wKingRow, wKingCol = gs.whiteKinglocation
    bKingRow, bKingCol = gs.blackKinglocation

    # Tránh để vua ở góc (0,0)...(7,7)
    centerBonus = [[0, 0, 1, 2, 2, 1, 0, 0],
                   [0, 1, 2, 3, 3, 2, 1, 0],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 4, 5, 5, 4, 3, 2],
                   [2, 3, 4, 5, 5, 4, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [0, 1, 2, 3, 3, 2, 1, 0],
                   [0, 0, 1, 2, 2, 1, 0, 0]]

    score += centerBonus[wKingRow][wKingCol] * 0.2
    score -= centerBonus[bKingRow][bKingCol] * 0.2

    return score

def findBestMove(gs, validMoves, returnQueue=None):
    """
    Tìm nước đi tốt nhất bằng Alpha-Beta pruning + đánh giá vị trí.
    Nếu returnQueue được truyền (dùng multiprocessing), sẽ dùng để trả kết quả.
    """
    global nextMove
    nextMove = None
    random.shuffle(validMoves)  # tránh lặp chiến lược

    turnMultiplier = 1 if gs.whiteToMove else -1
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, turnMultiplier)

    if returnQueue:
        returnQueue.put(nextMove)
    else:
        return nextMove
    
def detectThreats(gs):
    threats = []
    validOpponentMoves = gs.getValidMoves()
    for move in validOpponentMoves:
        if move.pieceCaptured != '--':
            threats.append((move.endRow, move.endCol))
    return threats


'''def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE # for bot worst score
    bestMoveForPlayer = None # for black
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove) # bot (black) makes a move
        opponentsMoves = gs.getValidMoves() # player (white) get all valid moves 
        opponentMaxScore = -CHECKMATE # player(opponent/white) worst possibility
        for opponentsMove in opponentsMoves:
            # the more positive the score the better the score for player(opponent)
            # player (opponent/white) makes a move for bot (black)
            gs.makeMove(opponentsMove) # player makes a move
            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE # if player (white) makes a move and it results in checkmate than its the max score for player but worst for bot
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore: # if player (opponent/white) moves does not result in checkmate(worst score for bot)
            ''''''
            opponentMaxScore = max score for the opponent if bot played playerMove

            it is calculating all possibles moves for player after bot makes move and store the minimum score of player after making player move in opponentMinMaxScore
            then again it check what if bot whould have played different move
            ''''''
            opponentMinMaxScore = opponentMaxScore
            bestMoveForPlayer = playerMove
        gs.undoMove()
    return bestMoveForPlayer '''

'''def findMoveMinMax(gs, validMoves, depth, whiteToMove): #depth represent how many moves ahead we want to look to find current best move
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE # worst score for white
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE # worst score for black
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore'''
# without alpha beta pruning
'''def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves() # opponent validmoves
        ''''''
        - sign because what ever opponents best score is, is worst score for us
        negative turnMultiplier because it changes turns after moves made 
        ''''''
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore'''

# calculate score of the board based on position
'''
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score
'''