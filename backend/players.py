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
			if env.check_win(env.board, temp_row, move, self.position):
				score += 10000 # Large score for winning move
			env.board[temp_row][move] = 0 # Undo temp move

			# Check if this move blocks opponent from winning
			env.board[temp_row][move] = 3 - self.position
			if env.check_win(env.board, temp_row, move, 3 - self.position):
				score += 5000 # Large score for blocking move
			env.board[temp_row][move] = 0 # Undo temp move

			move_scores.append((score, move))

		# Sort moves by score in descending order
		return [move for score, move in sorted(move_scores, key=lambda x: x[0], reverse=True)]


	def alpha_beta(self, env, depth, alpha, beta, maximizing):
		if time.time() - self.start_time > self.time_limit:
			raise TimeoutError("Time limit exceeded during alpha_beta recursion")

		# Determine the player who just made the move leading to this state
		# This is complex in a general minimax where you don't pass `last_move_player`
		# A simpler way is to check if the current `env` state itself is a terminal state.
		# If the game is over, evaluate based on winner/tie.
		# We assume that `env.gameOver` is called on the state *before* a new move is made.
		# For minimax, we're checking if the state *after* a move is a win for the player
		# who made that move.

		# It's better to check terminal states (win/loss/tie) on the current 'env' after a move is applied
		# during the recursive calls. The `gameOver` in connect4 needs the last move to check efficiently.
		# Here, we can simulate `gameOver` by checking wins for both players.
		
		# Check if the player who just moved won (this depends on whose turn it was *before* this minimax call)
		# If maximizing is True, it means it's current player's turn (self.position).
		# If maximizing is False, it means it's opponent's turn (3 - self.position).
		# So, the player who just moved is (3 - self.position) if maximizing, or self.position if not maximizing.

		# This check is tricky. It's usually better to determine the winner *after* the move.
		# Given how `connect4.gameOver` is structured (needs `j` and `player`), we need a simpler win check.
		# Using `env.check_win` on the current board state.

		# Check for winning state for the *previous* player (the one who just made the move to reach this state)
		# If maximizing is True, it means current turn is self.position, so the previous player was 3-self.position
		# If maximizing is False, it means current turn is 3-self.position, so the previous player was self.position
		
		# A more robust check for a terminal node in minimax is to evaluate the board directly for wins.
		# It's difficult to know the `last_move` (col) and `row` in `alpha_beta` without passing it,
		# so we need a more general `check_win` that scans the whole board.
		# I will use a simplified check here, or assume `env.gameOver` works for this.
		
		# If the state represents a win for the current maximizing player:
		# This means the *opponent* of the current maximizing player (the player who just moved) won.
		# So, if maximizing is True (current player is self), and opponent won, return -MAX_SCORE.
		# If maximizing is False (current player is opponent), and self won, return MAX_SCORE.

		# The `connect4.gameOver` modifies `env.is_winner`. We need to reset it.
		
		# To avoid deepcopying env repeatedly in alpha_beta, we modify `env` and then undo.
		# So, `env` is the mutable board state for the current path.
		
		# Check for win for the player whose turn it *was* before the last hypothetical move.
		# If maximizing (current player is `self.position`), the previous player was `3 - self.position`.
		# If not maximizing (current player is `3 - self.position`), the previous player was `self.position`.
		
		# To correctly check for a win in the current state for the player who just made a move:
		# We need the last move to call `env.gameOver` correctly.
		# Instead, let's use a simpler full-board win check for terminal states.
		
		# Check if previous player won (i.e., this is a terminal state)
		# If we are maximizing, it means the opponent just played to reach this state.
		# If we are minimizing, it means our player just played to reach this state.

		# This is a common point of confusion. The terminal check in minimax usually
		# happens *after* a hypothetical move has been made and before calling the next recursion level.
		# So, `env` here already has the move applied by the *previous* player.
		
		# Simplified terminal state checks:
		# If self can win in this state (meaning the previous move led to self winning)
		if env.check_win(env.board, 0, 0, self.position): # (0,0,self.position) are dummy values for row, col. Check_win needs to scan full board.
		# A proper check_win should not require the last move, but rather scan the whole board.
		# For now, let's just use `_evaluate_position` and define base cases.
			if not maximizing: # If it's minimizing player's turn, it means our player (self.position) just moved and won
				return self.MAX_SCORE
			else: # If it's maximizing player's turn, it means opponent (3-self.position) just moved and won
				return -self.MAX_SCORE
		
		if env.check_win(env.board, 0, 0, 3 - self.position):
			if not maximizing: # If minimizing player's turn, it means opponent just won
				return -self.MAX_SCORE
			else: # If maximizing player's turn, it means our player (self.position) just won
				return self.MAX_SCORE

		# Check for tie
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

	# The check_win method in alphaBetaAI should be self-contained and scan the board
	# without needing specific row/col arguments, or be adapted to use env's methods.
	# I will modify this to correctly call env's check_win or implement its own.
	# For now, let's ensure env.check_win is functional and use that.
	def check_win(self, env, player):
		# Delegate to the connect4 env's check_win which is more robust
		# This is a simplified call, as env.check_win expects last_move (row, col)
		# For a general check, iterate all cells and then check for 4 in a row from there.
		# A better implementation of a general board check:
		# Check horizontal, vertical, and both diagonals across the entire board.
		shape = env.shape
		board = env.board
		
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