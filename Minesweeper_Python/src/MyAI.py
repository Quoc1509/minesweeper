# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
# agent in this file. You will write the 'getAction' function,
# the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
# - DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
from collections import deque


class MyAI(AI):

    class Tiles():
        mine = False
        covered = True
        flag = False
        number = -10

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

        ########################################################################
        # YOUR CODE BEGINS						   #
        ########################################################################
        self.row = rowDimension
        self.col = colDimension
        self.totalMines = totalMines
        self.coveredTiles = rowDimension * colDimension

        self.startX = startX
        self.startY = startY

        self.rLast = startY
        self.cLast = startX
        self.lastTile = None

        self.safeQ = deque([])
        self.unknown = [(j, i) for i in range(self.row)
                        for j in range(self.col)]
        self.prob = dict()
        self.mines = []
        self.minesLeft = totalMines

        self.board = None

        self.lastAction = None
        self.flagsLeft = totalMines

        self.movesMade = 1
        self.movesLimit = 0

        self.createBoard()
        self.updateFirstMove()

        ########################################################################
        # YOUR CODE ENDS							   #
        ########################################################################

    def updateFirstMove(self):
        col = self.startX
        row = self.startY
        self.unknown.remove((col, row))
        self.cLast = col
        self.rLast = row
        self.board[col][row].covered = False
        self.board[col][row].number = 0
        self.lastTile = self.board[col][row]
        self.lastAction = AI.Action(1)

    def createBoard(self) -> None:
        """Create board with given dimensions"""
        self.board = [[self.Tiles() for i in range(self.row)]
                      for j in range(self.col)]
        self.movesLimit = self.col * self.row * 2 - 1

    def logLastMovePercept(self, number):
        """log the feedback percept number"""
        if self.lastAction == AI.Action(1):
            self.lastTile.covered = False
            self.lastTile.number = number

    def markMines(self, loc):
        col = loc[0]
        row = loc[1]
        if (col, row) not in self.mines:
            self.minesLeft -= 1
            self.mines.append((col, row))
            self.board[col][row].mine = True
            self.board[col][row].flag = True
            self.unknown.remove((col, row))

    def logMove(self, action, c, r):
        self.cLast = c
        self.rLast = r
        self.lastTile = self.board[c][r]
        self.lastAction = action
        self.movesMade += 1
        self.unknown.remove((c, r))
        if (c, r) in list(self.prob.keys()):
            self.prob.pop((c, r))

    def isInBound(self, col, row):
        if self.col > col and col >= 0 and self.row > row and row > 0:
            return True
        return False

    def surCovered(self, col, row):
        count = 0
        mines = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.isInBound(c, r):
                    if self.board[c][r].mine == True:
                        self.board[c][r].flag == True
                        count += 1
                        mines.append((c, r))
        return count, mines

    def surMines(self, col, row):
        count = 0
        mines = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.isInBound(c, r):
                    if self.board[c][r].mine == True:
                        self.board[c][r].flag = True
                        count += 1
                        mines.append((c, r))
        return count, mines

    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        # YOUR CODE BEGINS
        ########################################################################
        self.logLastMovePercept(number)

        if number == 0:
            # if the tile is in bound, not the last move, not in safeQ, and covered
            for col in range(self.cLast-1, self.cLast+2):
                for row in range(self.rLast-1, self.rlast+2):
                    if (self.isInBound(row, col) and (col != self.cLast and row != self.rLast)) and ((col, row) not in self.safeQ) and self.board[col][row].covered == True:
                        self.safeQ.append((col, row))

            # uncover all the safe tiles
            while self.safeQ != deque([]):
                cr = self.safeQ.popleft()
                self.logMove(AI.Action(1), cr[0], cr[1])
                return Action(AI.Action(1), cr[0], cr[1])

        for col in range(0, self.col):
            for row in range(0, self.row):
                if (self.board[col][row].covered == False and self.board[col][row].number != 0 and self.board[col][row].number == self.surCovered(col, row)[0]):
                    mines = self.surCovered(col, row)[1]
                    for i in mines:
                        self.markMines(i)

        for col in range(0, self.col):
            for row in range(0, self.row):
                if (self.board[col][row].number == self.surMines(col, row)[0]) and ((self.surCovered(col, row)[0] - self.surMines(col, row)[0]) > 0):
                    covered = self.surCovered(col, row)[1]
                    mines = self.surMines(col, row)[1]
                    for i in covered:
                        if i not in mines and i not in self.safeQ:
                            self.safeQ.append(i)

        while self.safeQ != deque([]):
            cr = self.safeQ.popleft()

            self.logMove(AI.Action(1), cr[0], cr[1])
            return Action(AI.Action(1), cr[0], cr[1])

        if self.minesLeft == 0:
            return Action(AI.Action(0))
        return Action(AI.Action.LEAVE)
        ########################################################################
        # YOUR CODE ENDS							   #
        ########################################################################
