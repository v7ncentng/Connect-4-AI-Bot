# players.py
import random
import time
import pygame
from copy import deepcopy
import math
from connect4 import connect4 # Ensure connect4 is imported for type hinting
import sys

# Global Pygame constants (ensure they are defined if not imported from connect4)
try:
	from connect4 import SQUARESIZE, BLUE, BLACK, P1COLOR, P2COLOR, ROW_COUNT, COLUMN_COUNT, width, height, size, RADIUS, screen
except ImportError:
	# Fallback/default definitions if not imported (e.g., for testing player logic directly)
	SQUARESIZE = 100
	BLUE = (0,0,255)
	BLACK = (0,0,0)
	P1COLOR = (255,0,0)
	P2COLOR = (255,255,0)
	ROW_COUNT = 6
	COLUMN_COUNT = 7
	width = COLUMN_COUNT * SQUARESIZE
	height = (ROW_COUNT+1) * SQUARESIZE
	size = (width, height)
	RADIUS = int(SQUARESIZE/2 - 5)
	screen = None # Screen will be initialized by connect4 if visualize is True

class connect4Player(object):
	def __init__(self, position, seed=0, CVDMode=False):
		self.position = position
		self.opponent = None # opponent will be set by the connect4 game instance
		self.seed = seed
		random.seed(seed)
		if CVDMode:
			global P1COLOR
			global P2COLOR
			P1COLOR = (227, 60, 239)
			P2COLOR = (0, 255, 0)

	def play(self, env: connect4, move_dict: dict) -> None:
		move_dict["move"] = -1

class humanConsole(connect4Player):
	'''
	Human player where input is collected from the console
	'''
	def play(self, env: connect4, move_dict: dict) -> None:
		while True:
			try:
				move = int(input('Select next move: '))
				if 0 <= move <= 6 and env.topPosition[move] >= 0:
					move_dict['move'] = move
					break
				else:
					print('Invalid move. Column is full or out of bounds. Please try again.')
			except ValueError:
				print('Invalid input. Please enter a number.')

class humanGUI(connect4Player):
	'''
	Human player where input is collected from the GUI
	'''
	def play(self, env: connect4, move_dict: dict) -> None:
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					if screen: # Ensure screen is initialized
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
					if 0 <= col <= 6 and env.topPosition[col] >= 0: # Validate move for GUI too
						move_dict['move'] = col
						done = True
					else:
						print("Invalid GUI move. Column is full or out of bounds.")


class randomAI(connect4Player):
	'''
	connect4Player that elects a random playable column as its move
	'''

	def play(self, env: connect4, move_dict: dict) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if indices: # Ensure there are possible moves
			move_dict['move'] = random.choice(indices)
		else:
			move_dict['move'] = 0 # Default to 0 if no moves, though randMove in connect4 handles this


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
		elif 0 in indices: # Added check for 0
			move_dict['move'] = 0
		else:
			# Fallback if none of preferred columns are available, pick any valid move
			if indices:
				move_dict['move'] = random.choice(indices)
			else:
				move_dict['move'] = 0 # Should not happen if game loop correctly checks for game over


class minimaxAI(connect4Player):

	def __init__(self, position, seed=0, CVDMode=False):
		super().__init__(position, seed, CVDMode) # Call parent constructor
		self.depth = 4 # Initialize depth

	def play(self, env: 'connect4', move_dict: dict) -> None:
		"""
		Make a move using the minimax algorithm.
		Updates move_dict['move'] with the chosen column.
		"""
		valid_moves = [i for i, pos in enumerate(env.topPosition) if pos >= 0]
		if not valid_moves:
			move_dict['move'] = 0
			return

		# Prioritize center column if empty for the very first move
		if all(env.board[r][c] == 0 for r in range(env.shape[0]) for c in range(env.shape[1])):
			if env.shape[1] // 2 in valid_moves:
				move_dict['move'] = env.shape[1] // 2
				return

		best_move = None
		best_score = float('-inf')

		# Iterate through possible moves and evaluate them
		for move in valid_moves:
			row_to_play = env.topPosition[move] # Get the specific row for this move
			if row_to_play >= 0:
				# Make the move on a deepcopy of the environment for simulation
				temp_env = deepcopy(env) # Create a deepcopy for each root move evaluation
				temp_env.board[row_to_play][move] = self.position
				temp_env.topPosition[move] -= 1

				score = self.minimax(temp_env, self.depth - 1, False) # Recursive call

				if score > best_score:
					best_score = score
					best_move = move

		move_dict['move'] = best_move if best_move is not None else valid_moves[0] # Fallback if no best move found

	def minimax(self, env: 'connect4', depth: int, maximizing: bool) -> float:

		# Terminal states
		# Check for win for the player who just moved
		# The player who just moved is the opposite of `maximizing`
		last_player = 3 - self.position if maximizing else self.position
		# This check needs to be more robust, as env doesn't store the *last* move easily
		# A better approach is to check for win conditions in general after a move.
		# For this structure, we'll assume `gameOver` is checked on the *current* env state.

		if env.gameOver(env.history[last_player-1][-1] if env.history[last_player-1] else -1, last_player):
			if env.is_winner:
				return 1000 if env.turnPlayer.opponent.position == self.position else -1000
			else: # It's a tie
				return 0

		if depth == 0:
			return self._evaluate_position(env)

		valid_moves = [i for i, pos in enumerate(env.topPosition) if pos >= 0]
		if not valid_moves:  # Board is full and no winner (tie)
			return 0

		if maximizing:
			value = float('-inf')
			for move in valid_moves:
				row_to_play = env.topPosition[move]
				if row_to_play >= 0:
					# Apply move
					env.board[row_to_play][move] = self.position
					env.topPosition[move] -= 1
					env.history[self.position-1].append(move) # Temporarily add to history for gameOver check

					value = max(value, self.minimax(env, depth - 1, False))

					# Undo move
					env.board[row_to_play][move] = 0
					env.topPosition[move] += 1
					env.history[self.position-1].pop()
			return value
		else: # Minimizing player
			value = float('inf')
			for move in valid_moves:
				row_to_play = env.topPosition[move]
				if row_to_play >= 0:
					# Apply move
					env.board[row_to_play][move] = 3 - self.position # Opponent's piece
					env.topPosition[move] -= 1
					env.history[ (3-self.position)-1 ].append(move) # Temporarily add to opponent's history

					value = min(value, self.minimax(env, depth - 1, True))

					# Undo move
					env.board[row_to_play][move] = 0
					env.topPosition[move] += 1
					env.history[ (3-self.position)-1 ].pop()
			return value

	def _check_winner(self, board, player: int, shape) -> bool:
		# Check horizontal
		for row in range(shape[0]):
			for col in range(shape[1] - 3):
				if all(board[row][col + i] == player for i in range(4)):
					return True

		# Check vertical
		for row in range(shape[0] - 3):
			for col in range(shape[1]):
				if all(board[row + i][col] == player for i in range(4)):
					return True

		# Check diagonal (positive slope)
		for row in range(shape[0] - 3):
			for col in range(shape[1] - 3):
				if all(board[row + i][col + i] == player for i in range(4)):
					return True

		# Check diagonal (negative slope)
		for row in range(3, shape[0]):
			for col in range(shape[1] - 3):
				if all(board[row - i][col + i] == player for i in range(4)):
					return True

		return False

	def _evaluate_position(self, env: 'connect4') -> float:
		score = 0

		# Evaluate center column preference
		center_col = env.shape[1] // 2
		center_array = [env.board[r][center_col] for r in range(env.shape[0])]
		center_count = center_array.count(self.position)
		score += center_count * 3

		# Evaluate windows (horizontal, vertical, diagonals)
		# Horizontal
		for r in range(env.shape[0]):
			for c in range(env.shape[1] - 3):
				window = [env.board[r][c+i] for i in range(4)]
				score += self._evaluate_window(window)

		# Vertical
		for c in range(env.shape[1]):
			for r in range(env.shape[0] - 3):
				window = [env.board[r+i][c] for i in range(4)]
				score += self._evaluate_window(window)

		# Positive diagonal
		for r in range(env.shape[0] - 3):
			for c in range(env.shape[1] - 3):
				window = [env.board[r+i][c+i] for i in range(4)]
				score += self._evaluate_window(window)

		# Negative diagonal
		for r in range(3, env.shape[0]):
			for c in range(env.shape[1] - 3):
				window = [env.board[r-i][c+i] for i in range(4)]
				score += self._evaluate_window(window)

		return score

	def _evaluate_window(self, window: list) -> float:
		score = 0
		player_count = window.count(self.position)
		opponent_count = window.count(3 - self.position)
		empty_count = window.count(0)

		if player_count == 4:
			score += 100
		elif player_count == 3 and empty_count == 1:
			score += 5
		elif player_count == 2 and empty_count == 2:
			score += 2

		if opponent_count == 3 and empty_count == 1:
			score -= 4
		# Consider blocking opponent's 2-in-a-row with 2 empty spaces more
		elif opponent_count == 2 and empty_count == 2:
			score -= 1

		return score


class alphaBetaAI(connect4Player):
	def __init__(self, position, seed=0, CVDMode=False):
		super().__init__(position, seed, CVDMode)
		self.transposition_table = {}
		self.MAX_SCORE = 1000000
		self.start_time = 0
		self.time_limit = 2.8  # Buffer for 3 second limit
		self.depth_limit = 8 # Max depth for iterative deepening

	def play(self, env: connect4, move_dict: dict) -> None:
		self.start_time = time.time()

		valid_moves = [i for i, pos in enumerate(env.topPosition) if pos >= 0]
		if not valid_moves:
			move_dict['move'] = 0
			return

		# Prioritize center column if empty for the very first move
		if all(env.board[r][c] == 0 for r in range(env.shape[0]) for c in range(env.shape[1])):
			if env.shape[1] // 2 in valid_moves:
				move_dict['move'] = env.shape[1] // 2
				return

		best_move = valid_moves[0] # Default best_move
		
		# Iterative deepening
		for depth in range(1, self.depth_limit + 1):
			try:
				current_best = self.find_best_move(env, valid_moves, depth)
				if current_best is not None:
					best_move = current_best # Update best_move if a deeper search completes
				
			except TimeoutError:
				# If timeout, use the best_move found at the previous depth
				break
			except Exception as e:
				print(f"Error during Alpha-Beta search at depth {depth}: {e}")
				break # Exit on other errors

		move_dict['move'] = best_move

	def find_best_move(self, env, moves, depth):
		if time.time() - self.start_time > self.time_limit:
			raise TimeoutError("Time limit exceeded during find_best_move")

		best_value = float('-inf')
		best_move = None
		alpha = float('-inf')
		beta = float('inf')

		ordered_moves = self.order_moves(env, moves)

		for move in ordered_moves:
			row = env.topPosition[move]
			if row >= 0:
				# Make move
				env.board[row][move] = self.position
				env.topPosition[move] -= 1
				env.history[self.position-1].append(move) # Add to history for win check

				value = self.alpha_beta(env, depth - 1, alpha, beta, False)

				# Undo move
				env.board[row][move] = 0
				env.topPosition[move] += 1
				env.history[self.position-1].pop()

				if value > best_value:
					best_value = value
					best_move = move
				alpha = max(alpha, value)

		return best_move

	def order_moves(self, env, valid_moves):
		move_scores = []
		center_col = env.shape[1] // 2
		
		for move in valid_moves:
			score = 0
			
			# Prefer center columns (heuristic)
			score += (env.shape[1] - abs(center_col - move)) * 3 # More central = higher score

			# Temporarily make the move to check for immediate wins/blocks
			temp_row = env.topPosition[move]
			if temp_row < 0: # Column is full, should have been caught by valid_moves, but as a safeguard
				continue

			# Check if this move wins the game for self
			env.board[temp_row][move] = self.position
			if self.check_win_at_position(env.board, temp_row, move, self.position, env.shape):
				score += 10000 # Large score for winning move
			env.board[temp_row][move] = 0 # Undo temp move

			# Check if this move blocks opponent from winning
			env.board[temp_row][move] = 3 - self.position
			if self.check_win_at_position(env.board, temp_row, move, 3 - self.position, env.shape):
				score += 5000 # Large score for blocking move
			env.board[temp_row][move] = 0 # Undo temp move

			move_scores.append((score, move))

		# Sort moves by score in descending order
		return [move for score, move in sorted(move_scores, key=lambda x: x[0], reverse=True)]

	def alpha_beta(self, env, depth, alpha, beta, maximizing):
		if time.time() - self.start_time > self.time_limit:
			raise TimeoutError("Time limit exceeded during alpha_beta recursion")

		# Check for terminal states
		# Check if current player (maximizing) won
		if maximizing:
			current_player = self.position
		else:
			current_player = 3 - self.position

		# Check if the opponent just won (the player who moved to reach this state)
		opponent_player = 3 - current_player
		if self.check_win_full_board(env.board, opponent_player, env.shape):
			if opponent_player == self.position:
				return self.MAX_SCORE
			else:
				return -self.MAX_SCORE

		# Check for tie (board full)
		valid_moves = [i for i, pos in enumerate(env.topPosition) if pos >= 0]
		if not valid_moves:
			return 0 # Tie

		if depth == 0:
			return self.evaluate_position(env)

		if maximizing:
			value = float('-inf')
			for move in valid_moves:
				row = env.topPosition[move]
				if row >= 0:
					env.board[row][move] = self.position
					env.topPosition[move] -= 1
					value = max(value, self.alpha_beta(env, depth - 1, alpha, beta, False))
					env.board[row][move] = 0 # Undo move
					env.topPosition[move] += 1
					alpha = max(alpha, value)
					if alpha >= beta:
						break
			return value
		else: # Minimizing player
			value = float('inf')
			for move in valid_moves:
				row = env.topPosition[move]
				if row >= 0:
					env.board[row][move] = 3 - self.position
					env.topPosition[move] -= 1
					value = min(value, self.alpha_beta(env, depth - 1, alpha, beta, True))
					env.board[row][move] = 0 # Undo move
					env.topPosition[move] += 1
					beta = min(beta, value)
					if alpha >= beta:
						break
			return value

	def check_win_at_position(self, board, row, col, player, shape):
		"""Check if placing a piece at (row, col) creates a win for player"""
		# Check horizontal
		for c in range(max(0, col - 3), min(col + 4, shape[1])):
			if c + 3 < shape[1]:
				if all(board[row][c + i] == player for i in range(4)):
					return True

		# Check vertical
		for r in range(max(0, row - 3), min(row + 4, shape[0])):
			if r + 3 < shape[0]:
				if all(board[r + i][col] == player for i in range(4)):
					return True

		# Check diagonal (positive slope)
		for i in range(-3, 4):
			r, c = row + i, col + i
			if 0 <= r < shape[0] - 3 and 0 <= c < shape[1] - 3:
				if all(board[r + j][c + j] == player for j in range(4)):
					return True

		# Check diagonal (negative slope)
		for i in range(-3, 4):
			r, c = row + i, col - i
			if 0 <= r < shape[0] - 3 and 0 <= c < shape[1] - 3:
				if all(board[r + j][c - j] == player for j in range(4)):
					return True
		return False

	def check_win_full_board(self, board, player, shape):
		"""Check if player has won anywhere on the board"""
		# Check horizontal
		for r in range(shape[0]):
			for c in range(shape[1] - 3):
				if all(board[r][c + i] == player for i in range(4)):
					return True

		# Check vertical
		for r in range(shape[0] - 3):
			for c in range(shape[1]):
				if all(board[r + i][c] == player for i in range(4)):
					return True

		# Check diagonal (positive slope)
		for r in range(shape[0] - 3):
			for c in range(shape[1] - 3):
				if all(board[r + i][c + i] == player for i in range(4)):
					return True

		# Check diagonal (negative slope)
		for r in range(3, shape[0]):
			for c in range(shape[1] - 3):
				if all(board[r - i][c + i] == player for i in range(4)):
					return True
		return False
		
	def evaluate_position(self, env):
		score = 0
		
		# Prioritize center column
		center_col = env.shape[1] // 2
		center_array = [env.board[r][center_col] for r in range(env.shape[0])]
		score += sum(1 for piece in center_array if piece == self.position) * 3
		
		# Evaluate windows
		# Horizontal
		for r in range(env.shape[0]):
			for c in range(env.shape[1] - 3):
				window = [env.board[r][c+i] for i in range(4)]
				score += self.evaluate_window(window)
				
		# Vertical
		for c in range(env.shape[1]):
			for r in range(env.shape[0] - 3):
				window = [env.board[r+i][c] for i in range(4)]
				score += self.evaluate_window(window)
				
		# Positive diagonal
		for r in range(env.shape[0] - 3):
			for c in range(env.shape[1] - 3):
				window = [env.board[r+i][c+i] for i in range(4)]
				score += self.evaluate_window(window)
				
		# Negative diagonal
		for r in range(3, env.shape[0]):
			for c in range(env.shape[1] - 3):
				window = [env.board[r-i][c+i] for i in range(4)]
				score += self.evaluate_window(window)
				
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
		# If opponent has 2 with 2 empty, give a small penalty to encourage blocking that progression
		elif opponent_pieces == 2 and empty_pieces == 2:
			score -= 1
			
		return score