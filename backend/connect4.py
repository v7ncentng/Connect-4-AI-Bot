# connect4.py
import numpy as np
import os, sys
import pygame
import random
from thread import thread_with_trace
from copy import deepcopy
import time

# Defining globals (moved to top for clarity and accessibility)
SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
P1COLOR = (255,0,0)
P2COLOR = (255,255,0)
WHITE = (255,255,255)

ROW_COUNT = 6
COLUMN_COUNT = 7

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = None # Initialize screen to None

def time_limit(func, args, timeout):
	'''
	Run func with given args and kill after timeout seconds
	'''
	t = thread_with_trace(target=func, args=args)
	t.start()
	t.join(timeout)
	if t.is_alive():
		t.kill()
		raise TimeoutError("Function call exceeded time limit") # Explicitly raise TimeoutError

class connect4():
	def __init__(self, player1, player2, board_shape=(6,7), visualize=False, game=0, save=False,
		limit_players=[-1,-1], time_limit=[-1,-1], verbose=False, CVDMode=False, print_time_logs = False):

		global screen # Declare screen as global here as well

		self.shape = board_shape
		self.visualize = visualize # show the GUI be displayed

		if self.visualize:
			pygame.init()
			screen = pygame.display.set_mode(size)

		# An array that is the same shape as the board.
		# 0 represents an available position,
		# 1 represents a postion occuppied by player1's piece,
		# 2 represents a position occupied by player2's piece
		# Initialized to all zeros, as no pieces have been played
		self.board = np.zeros(board_shape).astype('int32')

		# Array that is length of number of columns. Each value represents the position of
		# the first empty space in the column:
		# 6 means their are no pieces in this column
		# 0 means their is only the top position left
		# -1 means their are no empty spaces in this column
		self.topPosition = (np.ones(board_shape[1]) * (board_shape[0]-1)).astype('int32')
		self.player1 = player1
		self.player2 = player2
		# Ensure player objects have an opponent attribute
		self.player1.opponent = self.player2
		self.player2.opponent = self.player1

		self.is_winner = False # track if a the game has a winner

		self.visualize = visualize # show the GUI be displayed

		self.turnPlayer = self.player1 # which player's turn is it?
		self.history = [[], []] # track history of moves played for each player
		self.game = game # just an integer to track which number game this is for logging purposes
		self.save = save # should the results of this game be saved?
		self.limit = limit_players # are players are subject to a time limit for each move (-1 indicates no limit)
		self.time_limits = time_limit # time limits (in seconds) for each player
		self.verbose = verbose # controls how much info is printed to the console
		self.print_time_logs = print_time_logs

		# Make sure time limits are formatted acceptably
		if len(self.time_limits) != 2:
			self.time_limits = [0.5,0.5]
		if self.time_limits[0] <= 0:
			self.time_limits[0] = 0.5
		if self.time_limits[1] <= 0:
			self.time_limits[1] = 0.5

		# Just changes the color of the pieces if true
		if CVDMode:
			global P1COLOR
			global P2COLOR
			P1COLOR = (227, 60, 239)
			P2COLOR = (0, 255, 0)


	def playTurn(self):
		'''
		Get the next player's move and play it
		'''

		# Move is stored in a dict, so that it can be passed and updated by reference.
		move_dict = {"move" : self.randMove()}

		# If player should be time-limited, enforce a time limit
		start = time.time()
		try:
			if self.turnPlayer.position in self.limit:
				time_limit(self.turnPlayer.play, (self.getEnv(),move_dict,), self.time_limits[self.turnPlayer.position-1])
			else:
				self.turnPlayer.play(self.getEnv(), move_dict)

			if self.print_time_logs:
				print(f"Player {self.turnPlayer.position} move successfully completed in {round(time.time() - start, 2)}s")

		except TimeoutError:
			move_dict['move'] = self.randMove()
			if self.print_time_logs:
				print(f"Player {self.turnPlayer.position} move exceeded {self.time_limits[self.turnPlayer.position-1]}s time limit and was terminated. A random move will be chosen")


		move = move_dict["move"]

		# Correct illegal move (assign random)
		if not (0 <= move < self.shape[1] and self.topPosition[move] >= 0): # Check if move is within bounds and column is not full
			move = self.randMove()

		# Update board with move
		self.board[self.topPosition[move]][move] = self.turnPlayer.position

		# Track that position is no longer available
		self.topPosition[move] -= 1

		# Track move in history
		self.history[self.turnPlayer.position-1].append(move)

		# Change which player's turn it is
		self.turnPlayer = self.turnPlayer.opponent

		if self.visualize:
			self.draw_board()

		if self.verbose:
			print(self.board)

		return move

	def play(self):
		'''
		Base game loop
		'''
		if self.visualize:
			self.draw_board() # draw current state of the board

		# Get the first player's first move
		player = self.turnPlayer.position
		move = self.playTurn()

		# Play until the game is over
		while not self.gameOver(move, player):
			if self.visualize:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						pygame.quit()
						sys.exit()

			player = self.turnPlayer.position

			move = self.playTurn()

		# Record the moves that were made
		if self.save:
			self.saveGame()

		# Print out result of game
		winner = 0 # 0 represents a tie

		if self.is_winner:
			winner = self.turnPlayer.opponent.position

		if self.verbose:
			if self.is_winner:
				print('Player ', winner, ' has won')
			else:
				print('The game has tied')

		# Continue visualizing the board after game is over until GUI is closed
		spectating = True
		while spectating and self.visualize:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
					spectating = False
					break

		return winner

	# Method to simulate a move without modifying the actual game state directly
	def simulateMove(self, env_board, env_top_position, move: int, player: int):
		'''
		Play the move on a given board and topPosition array.
		This is a helper for AI simulations, not for actual game play.
		'''
		if env_top_position[move] >= 0:
			env_board[env_top_position[move]][move] = player
			env_top_position[move] -= 1
			return True
		return False

	def check_win(self, board, row, col, player):
		# Check horizontal
		for c in range(max(0, col - 3), min(col + 4, self.shape[1])):
			if c + 3 < self.shape[1]:
				if all(board[row][c + i] == player for i in range(4)):
					return True

		# Check vertical
		for r in range(max(0, row - 3), min(row + 4, self.shape[0])):
			if r + 3 < self.shape[0]:
				if all(board[r + i][col] == player for i in range(4)):
					return True

		# Check diagonal (positive slope)
		for i in range(-3, 4):
			r, c = row + i, col + i
			if 0 <= r < self.shape[0] - 3 and 0 <= c < self.shape[1] - 3:
				if all(board[r + j][c + j] == player for j in range(4)):
					return True

		# Check diagonal (negative slope)
		for i in range(-3, 4):
			r, c = row + i, col - i
			if 0 <= r < self.shape[0] - 3 and 0 <= c < self.shape[1] - 3:
				if all(board[r + j][c - j] == player for j in range(4)):
					return True
		return False

	def gameOver(self, j, player):
		'''
		Determine if the game is over or not.
		The game is over if:
		- There are 4 connected pieces of the same color in a row, column, or diagonal
		- All positions are filled and no one has won
		'''
		i = self.topPosition[j] + 1 # The row where the piece was just dropped

		if self.check_win(self.board, i, j, player):
			self.is_winner = True
			return True

		# If there are no 4 connected pieces, have all positions been filled?
		return len(self.history[0]) + len(self.history[1]) == self.shape[0]*self.shape[1]

	def saveGame(self):
		'''
		Save each players moves out to a text file
		'''
		os.makedirs('history', exist_ok=True) # Ensure history directory exists
		with open(os.path.join('history', 'game_'+str(self.game)+'_P1.txt'), 'w') as filehandle:
			for item in self.history[0]:
				filehandle.write('%s\n' % item)
		with open(os.path.join('history', 'game_'+str(self.game)+'_P2.txt'), 'w') as filehandle:
			for item in self.history[1]:
				filehandle.write('%s\n' % item)

	def randMove(self):
		'''
		Randomly select one of the available moves
		'''
		possible = self.topPosition >= 0 # which columns have empty spaces
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if not indices: # If no possible moves, this can happen if the board is full
			return -1 # Indicate no valid move
		return random.choice(indices) # pick a random column as the random move

	def getBoard(self):
		'''
		Create a copy of the board array
		'''
		return deepcopy(self.board)

	def getEnv(self):
		'''
		Create a copy of the entire connect4 instance
		'''
		return deepcopy(self)

	'''Pygame code used with permission from Keith Galli.
	Refer to https://github.com/KeithGalli/Connect4-Python for licensing'''

	def draw_board(self):
		'''
		Create the GUI representation of the current board state
		'''
		for c in range(self.shape[1]):
			for r in range(self.shape[0]):
				pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
				pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

		for c in range(self.shape[1]):
			for r in range(self.shape[0]):
				if self.board[r][c] == 1:
					pygame.draw.circle(screen, P1COLOR, (int((c)*SQUARESIZE+SQUARESIZE/2), height-int((self.shape[0]-1-r)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
				elif self.board[r][c] == 2:
					pygame.draw.circle(screen, P2COLOR, (int((c)*SQUARESIZE+SQUARESIZE/2), height-int((self.shape[0]-1-r)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
		pygame.display.update()

	# Added for app.py compatibility. These methods are not directly used by main.py
	def play_move(self, col):
		# This method assumes a player has already been set or it's a direct move
		# For direct usage with Flask app, it needs to know whose turn it is
		# or the Flask app needs to manage turns and player objects.
		# For simplicity, assuming player 1 makes the move if called directly.
		if self.topPosition[col] >= 0:
			self.board[self.topPosition[col]][col] = self.turnPlayer.position
			self.topPosition[col] -= 1
			self.history[self.turnPlayer.position-1].append(col)
			# After the move, switch turn for the next potential AI move
			self.turnPlayer = self.turnPlayer.opponent
			return True
		return False

	def get_valid_moves(self):
		return [i for i, pos in enumerate(self.topPosition) if pos >= 0]
	
	# The original _evaluate_position method from minimaxAI seems to be intended here.
	# However, since get_best_move is called directly on connect4 object in app.py,
	# it implies connect4 should have AI logic, which is usually not the case.
	# This method is likely a placeholder from refactoring.
	# For main.py to run, these are not strictly necessary as main.py uses player objects.
	# But for completeness, if app.py is to work, it would need a proper AI integrated.
	# For now, I'll remove the placeholder, as it's not well-defined for the connect4 class itself.
	# If app.py is to be used, its logic needs more thought to integrate AI players properly.