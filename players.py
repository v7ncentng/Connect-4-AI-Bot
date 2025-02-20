import random
import pygame
from copy import deepcopy
import math
from connect4 import connect4
import sys

class connect4Player(object):
	def __init__(self, position, seed=0, CVDMode=False):
		self.position = position
		self.opponent = None
		self.seed = seed
		self.weight = [[3, 4, 5, 5, 5, 4, 3], 
					   [4, 6, 8, 8, 8, 6, 4], 
					   [5, 8, 12, 15, 12, 8, 5], 
					   [5, 8, 12, 15, 12, 8, 5], 
					   [4, 6, 8, 10, 8, 6, 4], 
					   [3, 5, 10, 20, 10, 5, 3]]
		random.seed(seed)
		if CVDMode:
			global P1COLOR
			global P2COLOR
			P1COLOR = (227, 60, 239)
			P2COLOR = (0, 255, 0)

	def play(self, env: connect4, move_dict: dict) -> None:
		move_dict["move"] = -1

	def undo_move(self, col):
		"""Reverts the last move in the given column."""
		for row in range(self.shape[0]):
			if self.board[row][col] != 0:
				self.board[row][col] = 0  # Remove the piece
				self.topPosition[col] += 1  # Restore top position
				self.history[0].pop()  # Remove from history
				break

class humanConsole(connect4Player):
	'''
	Human player where input is collected from the console
	'''
	def play(self, env: connect4, move_dict: dict) -> None:
		move_dict['move'] = int(input('Select next move: '))
		while True:
			if int(move_dict['move']) >= 0 and int(move_dict['move']) <= 6 and env.topPosition[int(move_dict['move'])] >= 0:
				break
			move_dict['move'] = int(input('Index invalid. Select next move: '))

class humanGUI(connect4Player):
	'''
	Human player where input is collected from the GUI
	'''

	def play(self, env: connect4, move_dict: dict) -> None:
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
					posx = event.pos[0]
					if self.position == 1:
						pygame.draw.circle(screen, P1COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
					else: 
						pygame.draw.circle(screen, P2COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
				pygame.display.update()

				if event.type == pygame.MOUSEBUTTONDOWN:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
					move_dict['move'] = col
					done = True

class randomAI(connect4Player):
	'''
	connect4Player that elects a random playable column as its move
	'''

	def play(self, env: connect4, move_dict: dict) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		move_dict['move'] = random.choice(indices)

class stupidAI(connect4Player):
	'''
	connect4Player that will play the same strategy every time
	Tries to fill specific columns in a specific order 
	'''
	def play(self, env: connect4, move_dict: dict) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if 3 in indices:
			move_dict['move'] = 3
		elif 2 in indices:
			move_dict['move'] = 2
		elif 1 in indices:
			move_dict['move'] = 1
		elif 5 in indices:
			move_dict['move'] = 5
		elif 6 in indices:
			move_dict['move'] = 6
		else:
			move_dict['move'] = 0

class minimaxAI(connect4Player):
	'''
	This is where you will design a connect4Player that 
	implements the minimiax algorithm WITHOUT alpha-beta pruning
	'''
     
	def play(self, env: connect4, move_dict: dict) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		best_move = None
		best_score = float('-inf')
		for move in indices:
			temp_board.playTurn(move)
			score = self.minimax(temp_board, depth = 4, maximizing = False)
			temp_board.undo_move(move)
			if score > best_score:
				best_score = score
				best_move = move
		move_dict['move'] = best_move if best_move is not None else random.choice(indices)
  
	def minimax(self, env: connect4, depth: int, maximizing: bool) -> int:
     
		if depth == 0 or env.is_winner:
			return self.evaluate_board(env)
        
		possible_moves = [i for i in range(env.shape[1]) if env.topPosition[i] >= 0]
        
		if maximizing:
			max_eval = float('-inf')
			for move in possible_moves:
				temp_board.playTurn(move, self)
				score = self.minimax(temp_board, depth = 4, maximizing = False)
				temp_board.undo_move(move)
				eval = self.minimax(temp_board, depth - 1, False)
				max_eval = max(max_eval, eval)
				
			return max_eval
		else:
			min_eval = float('inf')
			for move in possible_moves:
				temp_board.playTurn(move)
				score = self.minimax(temp_board, depth = 4, maximizing = False)
				temp_board.undo_move(move)
				eval = self.minimax(temp_board, depth - 1, True)
				min_eval = min(min_eval, eval)
			return min_eval
  
  
class alphaBetaAI(connect4Player):
	def __init__(self, position, seed=0, CVDMode=False):
		super().__init__(position, seed, CVDMode)
		self.transposition_table = {}  # Cache for positions we've already evaluated
		self.MAX_SCORE = 1000000
		
	def play(self, env: connect4, move_dict: dict) -> None:
		max_depth = 6  # Increased depth since we've optimized the algorithm
		
		valid_moves = self.get_valid_moves(env)
		if not valid_moves:
			move_dict['move'] = 0
			return
			
		# Order moves by their initial evaluation
		move_scores = self.order_moves(env, valid_moves)
		ordered_moves = [move for _, move in move_scores]
		
		best_move = ordered_moves[0]  # Default to highest scored move
		
		# Iterative deepening with time control
		for current_depth in range(2, max_depth + 1):
			alpha = float('-inf')
			beta = float('inf')
			current_best_move = self.find_best_move(env, ordered_moves, current_depth, alpha, beta)
			
			if current_best_move is not None:
				best_move = current_best_move
		
		move_dict['move'] = best_move

	def get_valid_moves(self, env) -> list:
		"""Returns list of valid column moves."""
		return [i for i in range(env.shape[1]) if env.topPosition[i] >= 0]

	def order_moves(self, env, valid_moves) -> list:
		"""Orders moves based on initial evaluation."""
		move_scores = []
		for move in valid_moves:
			self.make_move(env, move, self.position)
			score = self.evaluate_quick(env)
			move_scores.append((score, move))
			self.undo_move(env, move)
			
		return sorted(move_scores, reverse=True)

	def find_best_move(self, env, moves, depth, alpha, beta) -> int:
		"""Finds the best move at the current depth."""
		best_value = float('-inf')
		best_move = None
		
		for move in moves:
			self.make_move(env, move, self.position)
			value = self.alpha_beta(env, depth - 1, alpha, beta, False)
			self.undo_move(env, move)
			
			if value > best_value:
				best_value = value
				best_move = move
			alpha = max(alpha, value)
			
		return best_move

	def alpha_beta(self, env, depth, alpha, beta, maximizing) -> int:
		"""Implements alpha-beta pruning algorithm."""
		board_hash = self.hash_position(env)
		
		if board_hash in self.transposition_table:
			cached_depth, cached_value = self.transposition_table[board_hash]
			if cached_depth >= depth:
				return cached_value
		
		# Check if this is a terminal state first
		if env.gameOver:
			return self.evaluate_terminal(env, depth)
			
		if depth == 0:
			return self.evaluate_position(env)
		
		valid_moves = self.get_valid_moves(env)
		value = float('-inf') if maximizing else float('inf')
		player = self.position if maximizing else 3 - self.position
		
		for move in valid_moves:
			self.make_move(env, move, player)
			child_value = self.alpha_beta(env, depth - 1, alpha, beta, False)
			self.undo_move(env, move)
			
			if maximizing:
				value = max(value, child_value)
				alpha = max(alpha, value)
			else:
				value = min(value, child_value)
				beta = min(beta, value)
				
			if alpha >= beta:
				break
		
		self.transposition_table[board_hash] = (depth, value)
		return value

	def make_move(self, env, col, player) -> None:
		"""Makes a move on the board."""
		env.board[env.topPosition[col]][col] = player
		env.topPosition[col] -= 1

	def undo_move(self, env, col) -> None:
		"""Undoes the last move made in the column."""
		env.topPosition[col] += 1
		env.board[env.topPosition[col]][col] = 0

	def evaluate_quick(self, env) -> int:
		"""Quick positional evaluation for move ordering."""
		score = 0
		for col in range(env.shape[1]):
			for row in range(env.shape[0]):
				if env.board[row][col] == self.position:
					score += self.weight[row][col]
		return score

	def evaluate_position(self, env) -> int:
		"""Thorough position evaluation for leaf nodes."""
		score = 0
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
		
		for row in range(env.shape[0]):
			for col in range(env.shape[1]):
				piece = env.board[row][col]
				if piece == 0:
					continue
				
				for dx, dy in directions:
					score += self.evaluate_line(env, row, col, dx, dy, piece)
		
		return score

	def evaluate_line(self, env, row, col, dx, dy, piece) -> int:
		"""Evaluates a line in a given direction."""
		count = 1
		blocked = 0
		
		# Check both directions
		for factor in [1, -1]:
			r, c = row + factor * dx, col + factor * dy
			while (0 <= r < env.shape[0] and 0 <= c < env.shape[1] and 
				count < 4):
				if env.board[r][c] != piece:
					if env.board[r][c] != 0:
						blocked += 1
					break
				count += 1
				r, c = r + factor * dx, c + factor * dy
		
		multiplier = 1 if piece == self.position else -1
		if count >= 4:
			return self.MAX_SCORE * multiplier
		elif count == 3 and blocked < 2:
			return 100 * multiplier
		elif count == 2 and blocked < 2:
			return 10 * multiplier
		return 0

	def evaluate_terminal(self, env, depth) -> int:
		"""Evaluates terminal game positions."""
		# Check for 4-in-a-row
		for row in range(env.shape[0]):
			for col in range(env.shape[1]):
				if env.board[row][col] == 0:
					continue
					
				# Check horizontal
				if col <= env.shape[1] - 4:
					if all(env.board[row][col+i] == self.position for i in range(4)):
						return self.MAX_SCORE + depth
					if all(env.board[row][col+i] == 3-self.position for i in range(4)):
						return -self.MAX_SCORE - depth
				
				# Check vertical
				if row <= env.shape[0] - 4:
					if all(env.board[row+i][col] == self.position for i in range(4)):
						return self.MAX_SCORE + depth
					if all(env.board[row+i][col] == 3-self.position for i in range(4)):
						return -self.MAX_SCORE - depth
				
				# Check diagonal right
				if col <= env.shape[1] - 4 and row <= env.shape[0] - 4:
					if all(env.board[row+i][col+i] == self.position for i in range(4)):
						return self.MAX_SCORE + depth
					if all(env.board[row+i][col+i] == 3-self.position for i in range(4)):
						return -self.MAX_SCORE - depth
				
				# Check diagonal left
				if col >= 3 and row <= env.shape[0] - 4:
					if all(env.board[row+i][col-i] == self.position for i in range(4)):
						return self.MAX_SCORE + depth
					if all(env.board[row+i][col-i] == 3-self.position for i in range(4)):
						return -self.MAX_SCORE - depth
		
		# If no winner, check if board is full (draw)
		if all(env.topPosition[col] < 0 for col in range(env.shape[1])):
			return 0
			
		# If we get here, game isn't over despite gameOver being True
		# Return a neutral evaluation
		return self.evaluate_position(env)

	def hash_position(self, env) -> str:
		"""Creates a unique hash of the current board state."""
		return ''.join(str(cell) for row in env.board for cell in row)


# Defining Constants
SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
P1COLOR = (255,0,0)
P2COLOR = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)




