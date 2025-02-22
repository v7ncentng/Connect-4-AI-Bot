import random
import time
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
		self.transposition_table = {}
		self.MAX_SCORE = 1000000
		self.start_time = 0
		self.time_limit = 2.8  # Buffer for 3 second limit
		
	def play(self, env: connect4, move_dict: dict) -> None:
		import time
		self.start_time = time.time()
		
		# Get valid moves using the environment's topPosition
		valid_moves = [i for i, pos in enumerate(env.topPosition) if pos >= 0]
		if not valid_moves:
			move_dict['move'] = 0
			return
			
		if all(env.board[env.shape[0]-1][col] == 0 for col in range(env.shape[1])):
			if 3 in valid_moves:
				move_dict['move'] = 3
				return
		
		best_move = valid_moves[0]
		depth = 1
		
		try:
			# Iterative deepening
			while time.time() - self.start_time < self.time_limit and depth <= 8:
				current_best = self.find_best_move(env, valid_moves, depth)
				if current_best is not None:
					best_move = current_best
				depth += 1
				
		except TimeoutError:
			pass
			
		move_dict['move'] = best_move
		
	def find_best_move(self, env, moves, depth):
		if time.time() - self.start_time > self.time_limit:
			raise TimeoutError
			
		best_value = float('-inf')
		best_move = None
		alpha = float('-inf')
		beta = float('inf')
		
		# Order moves with center preference
		ordered_moves = self.order_moves(env, moves)
		
		for move in ordered_moves:
			env_copy = env.getEnv()
			row = env_copy.topPosition[move]
			if row >= 0:  # Validity check
				env_copy.board[row][move] = self.position
				env_copy.topPosition[move] -= 1
				
				value = self.alpha_beta(env_copy, depth - 1, alpha, beta, False, move)
				
				if value > best_value:
					best_value = value
					best_move = move
				alpha = max(alpha, value)
			
		return best_move
		
	def order_moves(self, env, valid_moves):
		move_scores = []
		for move in valid_moves:
			if move < 0 or move >= env.shape[1]:  # Check valid column
				continue
				
			row = env.topPosition[move]
			if row < 0:  # Check if column is full
				continue
				
			score = 0
			
			# Prefer center columns
			score += (6 - abs(3 - move)) * 3
			
			# Check for winning move
			env_copy = env.getEnv()
			env_copy.board[row][move] = self.position
			if self.check_win(env_copy, row, move, self.position):
				score += 1000
				
			# Check for blocking move
			env_copy = env.getEnv()
			env_copy.board[row][move] = 3 - self.position
			if self.check_win(env_copy, row, move, 3 - self.position):
				score += 500
				
			move_scores.append((score, move))
			
		return [move for _, move in sorted(move_scores, reverse=True)]
		
	def check_win(self, env, row, col, player):
		# Horizontal
		count = 0
		for c in range(max(0, col-3), min(col+4, env.shape[1])):
			if env.board[row][c] == player:
				count += 1
			else:
				count = 0
			if count >= 4:
				return True
				
		# Vertical
		count = 0
		for r in range(max(0, row-3), min(row+4, env.shape[0])):
			if env.board[r][col] == player:
				count += 1
			else:
				count = 0
			if count >= 4:
				return True
				
		# Check Diagonal (positive slope)
		count = 0
		for i in range(-3, 4):
			r = row + i
			c = col + i
			if 0 <= r < env.shape[0] and 0 <= c < env.shape[1]:
				if env.board[r][c] == player:
					count += 1
				else:
					count = 0
				if count >= 4:
					return True
					
		# Check diagonal (negative slope)
		count = 0
		for i in range(-3, 4):
			r = row + i
			c = col - i
			if 0 <= r < env.shape[0] and 0 <= c < env.shape[1]:
				if env.board[r][c] == player:
					count += 1
				else:
					count = 0
				if count >= 4:
					return True
					
		return False
		
	def alpha_beta(self, env, depth, alpha, beta, maximizing, last_move):
		if time.time() - self.start_time > self.time_limit:
			raise TimeoutError
			
		if last_move is not None:
			last_row = 0
			for row in range(env.shape[0]):
				if env.board[row][last_move] != 0:
					last_row = row
					break
			if self.check_win(env, last_row, last_move, 3 - self.position if maximizing else self.position):
				return -self.MAX_SCORE if maximizing else self.MAX_SCORE
				
		if depth == 0:
			return self.evaluate_position(env)
			
		valid_moves = [i for i, pos in enumerate(env.topPosition) if pos >= 0]
		
		if not valid_moves:  # Draw
			return 0
			
		if maximizing:
			value = float('-inf')
			for move in valid_moves:
				row = env.topPosition[move]
				if row >= 0:
					env_copy = env.getEnv()
					env_copy.board[row][move] = self.position
					env_copy.topPosition[move] -= 1
					
					value = max(value, self.alpha_beta(env_copy, depth - 1, alpha, beta, False, move))
					alpha = max(alpha, value)
					if alpha >= beta:
						break
			return value
		else:
			value = float('inf')
			for move in valid_moves:
				row = env.topPosition[move]
				if row >= 0:
					env_copy = env.getEnv()
					env_copy.board[row][move] = 3 - self.position
					env_copy.topPosition[move] -= 1
					
					value = min(value, self.alpha_beta(env_copy, depth - 1, alpha, beta, True, move))
					beta = min(beta, value)
					if alpha >= beta:
						break
			return value
			
	def evaluate_position(self, env):
		score = 0
		
		for row in range(env.shape[0]):
			for col in range(env.shape[1] - 3):
				window = [env.board[row][col+i] for i in range(4)]
				score += self.evaluate_window(window)
				
		for row in range(env.shape[0] - 3):
			for col in range(env.shape[1]):
				window = [env.board[row+i][col] for i in range(4)]
				score += self.evaluate_window(window)
				
		for row in range(env.shape[0] - 3):
			for col in range(env.shape[1] - 3):
				window = [env.board[row+i][col+i] for i in range(4)]
				score += self.evaluate_window(window)
				
		for row in range(3, env.shape[0]):
			for col in range(env.shape[1] - 3):
				window = [env.board[row-i][col+i] for i in range(4)]
				score += self.evaluate_window(window)
				
		center_col = env.shape[1] // 2
		center_array = [env.board[row][center_col] for row in range(env.shape[0])]
		score += sum(1 for piece in center_array if piece == self.position) * 3
		
		return score
		
	def evaluate_window(self, window):
		score = 0
		player_pieces = window.count(self.position)
		opponent_pieces = window.count(3 - self.position)
		empty_pieces = window.count(0)
		
		if player_pieces == 4:
			score += 100
		elif player_pieces == 3 and empty_pieces == 1:
			score += 5
		elif player_pieces == 2 and empty_pieces == 2:
			score += 2
			
		if opponent_pieces == 3 and empty_pieces == 1:
			score -= 4
			
		return score
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




