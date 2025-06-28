import random
import json
import os

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
DEPTH = 5
CHECKMATE = 100000
STALEMATE = 0

# (giống phần đã có trước đó)
centerSquares = {(3, 3), (3, 4), (4, 3), (4, 4)}

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

blackPawnScores = whitePawnScores[::-1]

piecePositionScores = {
    "N": knightScores, "B": bishopScores, "Q": queenScores,
    "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores
}

# === ZOBRIST HASHING ===
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

TT_CACHE = {}  # Transposition Table

# === SCORE BOARD ===
def scoreBoard(gs):
    if gs.checkmate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    pieceCount = 0
    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece != "--":
                pieceType = piece[1]
                pieceColor = 1 if piece[0] == 'w' else -1
                pieceValue = pieceScore.get(pieceType, 0)
                posValue = 0

                if pieceType == "p":
                    key = piece
                    if key in piecePositionScores:
                        posValue = piecePositionScores[key][r][c]
                elif pieceType in piecePositionScores:
                    posValue = piecePositionScores[pieceType][r][c]

                score += pieceColor * (pieceValue + posValue * 0.1)
                pieceCount += 1

                if (r, c) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    score += 0.2 * pieceColor

    if pieceCount < 10:
        score += kingActivityScore(gs)

    return score

def kingActivityScore(gs):
    score = 0
    wKingRow, wKingCol = gs.whiteKinglocation
    bKingRow, bKingCol = gs.blackKinglocation
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

def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves, returnQueue=None):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    turnMultiplier = 1 if gs.whiteToMove else -1
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, turnMultiplier)
    if returnQueue:
        returnQueue.put(nextMove)
    else:
        return nextMove

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

# === PHÂN TÍCH ===
def isMoveDangerous(gs, move):
    gs.makeMove(move)
    opponentMoves = gs.getValidMoves()
    danger = any(m.endRow == move.endRow and m.endCol == move.endCol for m in opponentMoves)
    gs.undoMove()
    return danger

def analyzeMistakes(gs):
    mistakes = []
    for i in range(len(gs.moveLog) - 1):
        move = gs.moveLog[i]
        gs.makeMove(move)
        opponentMoves = gs.getValidMoves()
        for om in opponentMoves:
            if om.endRow == move.endRow and om.endCol == move.endCol and om.pieceCaptured != '--':
                mistakes.append((i + 1, str(move), om.pieceCaptured))
                break
        gs.undoMove()
    return mistakes
