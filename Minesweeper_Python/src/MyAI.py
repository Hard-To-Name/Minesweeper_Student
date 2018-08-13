from AI import AI
from Action import Action
from collections import deque
from queue import PriorityQueue

class MyAI( AI ):

	# Tile class
	class __Tile():
		mine = False
		covered = True
		flag = False
		number = -1

	class __MinQ(object):
		def __init__(self, x, y, p):
			self.x = x
			self.y = y
			self.p = p
			return

		def __lt__(self, other):
			return self.p < other.p

		def __le__(self, other):
			return self.p <= other.p

		def __eq__(self, other):
			return self.p == other.p

		def __gt__(self, other):
			return self.p > other.p

		def __ge__(self, other):
			return self.p >= other.p

		def __str__(self):
			return "({},{},{})".format(self.p, self.x, self.y)

	class __MaxQ(object):
		def __init__(self, x, y, p):
			self.x = x
			self.y = y
			self.p = p
			return

		def __lt__(self, other):
			return self.p > other.p

		def __le__(self, other):
			return self.p >= other.p

		def __eq__(self, other):
			return self.p == other.p

		def __gt__(self, other):
			return self.p <= other.p

		def __ge__(self, other):
			return self.p <= other.p

		def __str__(self):
			return "({},{},{})".format(self.p, self.x, self.y)


	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines

		self.__lastX = startX
		self.__lastY = startY
		self.__lastAction = AI.Action.UNCOVER
		self.__totalFlagged = 0
		self.__totalUncovered = 1

		self.__createBoard()
		self.__uncoverQueue = deque()
		self.__flagQueue = deque()
		self.__steps = [(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0)]

	def getAction(self, number: int) -> "Action Object":
		if self.__lastAction == AI.Action.UNCOVER:

			(x, y) = (self.__lastX, self.__lastY)

			self.__board[x][y].number = number
			self.__board[x][y].covered = False

			if number == 0:
				for i in range(len(self.__steps)):
					self.__enqueue(self.__uncoverQueue, x + self.__steps[i][0], y + self.__steps[i][1])

		elif self.__lastAction == AI.Action.FLAG:
			(x, y) = (self.__lastX, self.__lastY)
			self.__board[x][y].covered = False
			self.__board[x][y].flag = True

		if self.__totalUncovered == self.__rowDimension * self.__colDimension:
			return Action(AI.Action.LEAVE)

		if len(self.__uncoverQueue) == 0 and len(self.__flagQueue) == 0:
			self.__sweep();
			if len(self.__uncoverQueue) == 0 and len(self.__flagQueue) == 0:
				self.__deepSweep()
				if len(self.__uncoverQueue) == 0 and len(self.__flagQueue) == 0:
					self.__AISweep()

		if len(self.__uncoverQueue) != 0:
			(self.__lastX,self.__lastY) = self.__uncoverQueue.popleft()
			self.__lastAction = AI.Action.UNCOVER
			self.__totalUncovered += 1
			action = Action(AI.Action.UNCOVER, self.__lastX, self.__lastY)
		elif len(self.__flagQueue) != 0:
			(self.__lastX, self.__lastY) = self.__flagQueue.popleft()
			self.__lastAction = AI.Action.FLAG
			self.__totalFlagged += 1
			self.__totalUncovered += 1
			action = Action(AI.Action.FLAG, self.__lastX, self.__lastY)
		else:
			action = Action(AI.Action.LEAVE)

#		self.__printBoard()

		return action


	def __createBoard(self):
		self.__board = [[self.__Tile() for i in range(self.__rowDimension)] for j in range(self.__colDimension)]

	def __printBoard(self):
		print("\nMY AI BOARD:")
		for i in range(self.__rowDimension - 1, -1, -1):
			print("   ", end=" ")
			for j in range(self.__colDimension):

				if not self.__board[j][i].covered and self.__board[j][i].flag:
					print('B ', end=" ")
				elif not self.__board[j][i].covered:
					print(str(self.__board[j][i].number) + ' ', end=" ")
				elif self.__board[j][i].flag:
					print('? ', end=" ")
				elif self.__board[j][i].covered:
					print('. ', end=" ")

			print('\n', end="")
		print()

	def _is_valid_col(self, col: int) -> bool:
		return 0 <= col < self.__colDimension


	def _is_valid_row(self, row: int) -> bool:
		return 0 <= row < self.__rowDimension


	def _is_valid(self, col: int, row: int):
		return self._is_valid_col(col) and self._is_valid_row(row)


	def _counters(self, col: int , row: int):
		covered = 0
		flags = 0
		for i in range(len(self.__steps)):
			(x, y) = (col + self.__steps[i][0], row + self.__steps[i][1])

			if self._is_valid(x, y):
				if self.__board[x][y].covered:
					covered += 1
				elif self.__board[x][y].flag:
					flags += 1
		return (covered, flags)


	def __enqueue(self, queue: deque, col: int, row: int):
		if self._is_valid(col, row):
			if self.__board[col][row].covered:
				if (col,row) not in queue:
					queue.append((col, row))

	def __sweep(self):
		if self.__totalFlagged == self.__totalMines:
			for i in range(self.__colDimension):
				for j in range(self.__rowDimension):
					if self.__board[i][j].covered:
						self.__enqueue(self.__uncoverQueue, i, j)
						return

		for i in range(self.__colDimension):
			for j in range(self.__rowDimension):
				if self.__board[i][j].number > 0:
					(covered, flagged) = self._counters(i, j)
					if self.__board[i][j].number == flagged:
						for k in range(len(self.__steps)):
							(x, y) = (i + self.__steps[k][0], j + self.__steps[k][1])
							if self._is_valid(x, y) and self.__board[x][y].covered:
								self.__enqueue(self.__uncoverQueue, x, y)

					elif self.__board[i][j].number  == covered + flagged:
						for k in range(len(self.__steps)):
							(x, y) = (i + self.__steps[k][0], j + self.__steps[k][1])
							if self._is_valid(x, y) and self.__board[x][y].covered:
								self.__enqueue(self.__flagQueue, x, y)


	def __deepSweep(self):
		for i in range(self.__colDimension):
			for j in range(self.__rowDimension):
				if self.__board[i][j].number > 0:
					covered = self.__getCovered(i, j)
					if len(covered) > 1:
						self.__examine(i, j, covered)


	def __examine(self, x: int, y: int, covered: list):
		(neighborList, commonList) = self.__getNeighborCommonList(x, y, covered)

		(c, f) = self._counters(x, y)
		for k in range(len(neighborList)):
			n = neighborList[k]
			(cn, fn) = self._counters(n[0], n[1])

			common = commonList[k]
			n_remaining = self.__board[n[0]][n[1]].number - fn
			n_nonmine = cn - n_remaining
			remaining = self.__board[x][y].number - f

			if remaining - n_remaining >= c - len(common):
				for z in covered:
					if not z in common:
						self.__enqueue(self.__flagQueue, z[0], z[1])

			if len(common) - n_nonmine >= remaining:
				for z in covered:
					if not z in common:
						self.__enqueue(self.__uncoverQueue, z[0], z[1])


	def __getNeighborCommonList(self, col: int, row: int, covered: list):
		neighborList = [];
		commonList = [];

		uncovered =  self.__getUncovered(col, row)
		for u in uncovered:
			tmpNeighbor = self.__getCovered(u[0], u[1])
			common = [n for n in tmpNeighbor if n in covered]

			if len(common) > 1:
				neighborList.append(u)
				commonList.append(common)

		return (neighborList, commonList)

	def __getCovered(self, col: int, row: int):
		result = []
		for k in range(len(self.__steps)):
			(x, y) = (col + self.__steps[k][0], row + self.__steps[k][1])
			if self._is_valid(x, y) and self.__board[x][y].covered:
				result.append((x,y))
		return result

	def __getUncovered(self, col: int, row: int):
		result = []
		for k in range(len(self.__steps)):
			(x, y) = (col + self.__steps[k][0], row + self.__steps[k][1])
			if self._is_valid(x, y):
				if self.__board[x][y].number > 0:
					result.append((x,y))
		return result


	def __AISweep(self):
		minQ = PriorityQueue()
		maxQ = PriorityQueue()
		for i in range(self.__colDimension):
			for j in range(self.__rowDimension):
				if self.__board[i][j].covered:
					min = 1.0
					max = 0.0
					uncovered = self.__getUncovered(i, j)

					if len(uncovered) == 0:
						continue

					l = []
					for u in uncovered:
						(c, f) = self._counters(u[0], u[1])
						p = (self.__board[u[0]][u[1]].number - f) / c
						l.append((i,j,p))

					avg = self.__avgP(l)
					minQ.put(self.__MinQ(i, j, avg))
					maxQ.put(self.__MaxQ(i, j, avg))

		if not minQ.empty() and not maxQ.empty():
			cmin = minQ.get()
			cmax = maxQ.get()
			if cmin.p <= 1.0 - cmax.p:
				self.__enqueue(self.__uncoverQueue, cmin.x, cmin.y)
			else:
				self.__enqueue(self.__flagQueue, cmax.x, cmax.y)
		elif not minQ.empty():
			cmin = minQ.get()
			self.__enqueue(self.__uncoverQueue, cmin.x, cmin.y)
		elif not maxQ.empty():
			cmax = maxQ.get()
			self.__enqueue(self.__flagQueue, cmax.x, cmax.y)


	def __avgP(self, l: list):
		total = 0
		for (x,y,p) in l:
			total += p
		return total/len(l)
