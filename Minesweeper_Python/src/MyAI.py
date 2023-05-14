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

    # Tile class
    class __Tile():
        mine = False
        covered = True
        flag = False
        number = -100

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

        self.row = rowDimension
        self.col = colDimension
        self.totalMines = totalMines
        self.coveredTiles = rowDimension * colDimension
        self.letMove = 1
        self.limitMove = 0
        self.cLast = startX
        self.rLast = startY
        self.lastTile = None
        self.lastAction = None
        self.flagsLeft = totalMines
        self.startX = startX
        self.startY = startY
        self.available = deque([])
        self.unknown = [(j, i) for i in range(self.row)
                        for j in range(self.col)]
        self.prob = dict()
        self.mines = []
        self.minesLeft = totalMines
        self.board = None
        self.createTable()
        self.firstMove()

    def lastMoveHint(self, number):
        if self.lastAction == AI.Action(1):
            self.lastTile.covered = False
            self.lastTile.number = number

    def inBounds(self, c, r) -> bool:
        if c < self.col and c >= 0 and r < self.row and r >= 0:
            return True
        return False

    def logMove(self, action, col, row):
        self.cLast = col
        self.rLast = row
        self.lastTile = self.board[col][row]
        self.lastAction = action
        self.letMove += 1
        self.unknown.remove((col, row))
        if (col, row) in list(self.prob.keys()):
            self.prob.pop((col, row))

    def arroundCovered(self, col, row):
        count = 0
        covered = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.inBounds(c, r) and (c, r) != (col, row):
                    if self.board[c][r].covered == True:
                        count += 1
                        covered.append((c, r))
        return count, covered

    def theMines(self, loc):
        col = loc[0]
        row = loc[1]
        if (col, row) not in self.mines:
            self.minesLeft -= 1
            self.mines.append((col, row))
            self.board[col][row].mine = True
            self.board[col][row].flag = True
            self.unknown.remove((col, row))

    def arroundMines(self, col, row):
        count = 0
        mine_num = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.inBounds(c, r):
                    if self.board[c][r].mine == True:
                        self.board[c][r].flag = True
                        count += 1
                        mine_num.append((c, r))
        return count, mine_num

    def arroundUnknown(self, col, row):
        count = 0
        noFlag = []
        for c in range(col-1, col+2):
            for r in range(row-1, row+2):
                if self.inBounds(c, r) and (c, r) != (col, row):
                    if self.known((c, r)) == False:
                        count += 1
                        noFlag.append((c, r))
        return count, noFlag

    def neighbor_test(self, col, row):
        safe = []
        center = (col, row)
        num_center = self.board[col][row].number

        neighbors_list = []
        for c in range(col-2, col+3):
            for r in range(row-2, row+3):
                if self.inBounds(c, r) == True and (c, r) != (col, row):
                    neighbors_list.append((c, r))
        neighbors = set(neighbors_list)

        for neighbor in neighbors:
            neighbor_arround = self.board[neighbor[0]][neighbor[1]].number
            if neighbor_arround < 1:
                continue

            N = self.arroundTiles(neighbor)
            if center in N:
                N.remove(center)
            if self.set_known(N) == True:
                continue

            A = self.arroundTiles(center)
            if neighbor in A:
                A.remove(neighbor)
            NnotA = N.difference(A)
            AnotN = A.difference(N)
            mine_of_A = set(self.arroundMines(center[0], center[1])[1])
            mine_of_N = set(self.arroundMines(neighbor[0], neighbor[1])[1])
            mines_both = mine_of_A.intersection(N)
            mines_A_not_N = mine_of_A.intersection(AnotN)
            mines_N_not_A = mine_of_N.intersection(NnotA)
            percept_both = len(mines_both)
            percept_A_not_N = len(mines_A_not_N)
            percept_N_not_A = len(mines_N_not_A)

            if self.set_known(NnotA) == False:
                continue
            if percept_N_not_A == 0 and percept_both == 0:
                continue
            if (num_center - percept_A_not_N) == (neighbor_arround - percept_N_not_A):
                for loc in AnotN:
                    if self.known(loc) == False:
                        safe.append(loc)
        return safe

    def constraints(self):
        constraints = []
        for col in range(self.col):
            for row in range(self.row):
                if self.board[col][row].number > 0 and self.arroundUnknown(col, row)[0] > 0:
                    constraints.append((col, row))
        return constraints

    def frontier(self):
        frontier = []
        for i in self.unknown:
            col = i[0]
            row = i[1]
            loc = (col, row)
            if (len(self.arroundTiles(loc)) - self.arroundCovered(col, row)[0] > 0):
                frontier.append(i)
        return frontier

    def firstMove(self) -> None:
        col = self.startX
        row = self.startY
        self.unknown.remove((col, row))
        self.cLast = col
        self.rLast = row
        self.board[col][row].covered = False
        self.board[col][row].nubmer = 0
        self.lastTile = self.board[col][row]
        self.lastAction = AI.Action(1)

    def createTable(self) -> None:
        self.board = [[self.__Tile() for i in range(self.row)]
                      for j in range(self.col)]
        self.limitMove = self.col * self.row * 2 - 1

    def arroundTiles(self, loc):
        tiles = set()
        for col in range(loc[0]-1, loc[0]+2):
            for row in range(loc[1]-1, loc[1]+2):
                if self.inBounds(col, row) and (col, row) != loc:
                    tiles.add((col, row))
        return tiles

    def set_known(self, set):
        for i in set:
            if self.known(i) == False:
                return False
        return True

    def known(self, loc):
        if self.board[loc[0]][loc[1]].covered == True and self.board[loc[0]][loc[1]].flag == False:
            return False
        return True

    def countMix(self, row):
        ones = 0
        neg_ones = 0
        onesList = []
        negList = []
        for i in range(len(row)):
            if row[i] == 1:
                ones += 1
                onesList.append(i)
            if row[i] == -1:
                neg_ones += 1
                negList.append(i)
        return ones, onesList, neg_ones, negList

    def reduce(self, matrix):
        j = 0
        row_num = len(matrix)
        column_num = len(matrix[0])
        for row in range(row_num):
            if j >= column_num:
                return
            i = row
            while matrix[i][j] == 0:
                i += 1
                if i == row_num:
                    i = row
                    j += 1
                    if column_num == j:
                        return
            matrix[i], matrix[row] = matrix[row], matrix[i]
            level = matrix[row][j]
            matrix[row] = [int(_ / level) for _ in matrix[row]]
            for i in range(row_num):
                if i != row:
                    level = matrix[i][j]
                    matrix[i] = [iv-level*rv for rv,
                                 iv in zip(matrix[row], matrix[i])]
            j += 1

    def condition1(self):
        for col in range(self.cLast-1, self.cLast+2):
            for row in range(self.rLast-1, self.rLast+2):
                if (self.inBounds(col, row) and
                        not (col == self.cLast and row == self.rLast)) and ((col, row) not in self.available) and self.board[col][row].covered == True:
                    self.available.append((col, row))

    def getAction(self, number: int) -> "Action Object":
        self.lastMoveHint(number)
        try:
            if (number == 0):
                self.condition1()
                # for col in range(self.cLast-1, self.cLast+2):
                #     for row in range(self.rLast-1, self.rLast+2):
                #         if (self.inBounds(col, row) and
                #                 not (col == self.cLast and row == self.rLast)) and ((col, row) not in self.available) and self.board[col][row].covered == True:
                #             self.available.append((col, row))

            while (self.available != deque([])):
                coord = self.available.popleft()
                self.logMove(AI.Action(1), coord[0], coord[1])
                return Action(AI.Action(1), coord[0], coord[1])

            for col in range(0, self.col):
                for row in range(0, self.row):
                    if (self.board[col][row].covered == False and
                        self.board[col][row].number != 0 and
                        self.board[col][row].number ==
                            self.arroundCovered(col, row)[0]):

                        mines = self.arroundCovered(col, row)[1]
                        for i in mines:
                            self.theMines(i)
            for col in range(0, self.col):
                for row in range(0, self.row):
                    if ((self.board[col][row].number ==
                        self.arroundMines(col, row)[0]) and
                        (self.arroundCovered(col, row)[0] -
                            self.arroundMines(col, row)[0] > 0)):
                        covered = self.arroundCovered(col, row)[1]
                        mines = self.arroundMines(col, row)[1]
                        for i in covered:
                            if (i not in mines) and (i not in self.available):
                                self.available.append(i)

            while (self.available != deque([])):
                coord = self.available.popleft()
                self.logMove(AI.Action(1), coord[0], coord[1])
                return Action(AI.Action(1), coord[0], coord[1])

            for col in range(self.col):
                for row in range(self.row):
                    if self.board[col][row].number > 0 and self.arroundUnknown(col, row)[0] > 0:
                        neigh = self.neighbor_test(col, row)
                        if neigh is not None and neigh != []:
                            for i in neigh:
                                if i in self.unknown and i not in self.available:
                                    self.available.append(i)

            while (self.available != deque([])):
                coord = self.available.popleft()
                self.logMove(AI.Action(1), coord[0], coord[1])
                return Action(AI.Action(1), coord[0], coord[1])

            constraints = []
            frontier = []

            unknown = self.unknown
            totalMinesLeft = self.minesLeft

            constraints = self.constraints()
            constraintsCount = len(constraints)

            frontier = self.frontier()

            rowCount = constraintsCount + 1
            columnCount = len(unknown) + 1

            if columnCount != 1 and rowCount != 1:
                columnHeader = [x for x in range(columnCount)]
                frontierHeader = columnHeader[:-1]
                col_to_tile = dict(zip(frontierHeader, unknown))
                tile_to_col = dict(zip(unknown, frontierHeader))
                matrix = [[0 for i in range(columnCount)]
                          for j in range(rowCount)]
                row = 0
                for constraint in constraints:
                    sub_frontier = self.arroundUnknown(
                        constraint[0], constraint[1])[1]
                    for tile in sub_frontier:
                        col = tile_to_col.get(tile)
                        matrix[row][col] = 1
                    minesCount = self.board[constraint[0]][constraint[1]
                                                           ].number - self.arroundMines(constraint[0], constraint[1])[0]
                    matrix[row][-1] = minesCount
                    row += 1
                for i in range(columnCount):
                    matrix[row][i] = 1
                matrix[-1][-1] = totalMinesLeft
                self.reduce(matrix)
                safe = []
                mines = []
                for row in matrix:
                    last = row[-1]
                    onesCount = self.countMix(row[:-1])[0]
                    onesList = self.countMix(row[:-1])[1]
                    neg_onesCount = self.countMix(row[:-1])[2]
                    negList = self.countMix(row[:-1])[3]
                    if last == 0:
                        if onesCount > 0 and neg_onesCount == 0:
                            for col in onesList:
                                tile = col_to_tile.get(col)
                                if tile not in safe:
                                    safe.append(tile)
                        if neg_onesCount > 0 and onesCount == 0:
                            for col in negList:
                                tile = col_to_tile.get(col)
                                if tile not in mines:
                                    mines.append(tile)
                    if last > 0:
                        if onesCount == last:
                            for col in onesList:
                                tile = col_to_tile.get(col)
                                if tile not in safe:
                                    mines.append(tile)
                            for col in negList:
                                tile = col_to_tile.get(col)
                                if tile not in mines:
                                    safe.append(tile)
                    if last < 0:
                        if neg_onesCount == last:
                            for col in onesList:
                                tile = col_to_tile.get(col)
                                if tile not in safe:
                                    safe.append(tile)
                            for col in negList:
                                tile = col_to_tile.get(col)
                                if tile not in mines:
                                    mines.append(tile)
                if mines != []:
                    for i in mines:
                        self.theMines(i)

                if safe != []:
                    for i in safe:
                        if i in self.unknown and i not in self.available:
                            self.available.append(i)

            while (self.available != deque([])):
                coord = self.available.popleft()
                self.logMove(AI.Action(1), coord[0], coord[1])
                return Action(AI.Action(1), coord[0], coord[1])

            if (self.minesLeft == 0):
                return Action(AI.Action(0))

            while (self.available != deque([])):
                coord = self.available.popleft()
                self.logMove(AI.Action(1), coord[0], coord[1])
                return Action(AI.Action(1), coord[0], coord[1])

            if (self.minesLeft == 0):
                return Action(AI.Action(0))
        except (ValueError, IndexError):
            print('!!! ValueError or IndexError in getAction')
            raise
