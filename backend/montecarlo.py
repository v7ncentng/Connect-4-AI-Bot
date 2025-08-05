# montecarlo.py
import numpy as np
import random
from players import connect4Player
from connect4 import connect4
from copy import deepcopy

class monteCarloAI(connect4Player):
	'''
	For each legal first_move, monteCarloAI will simulate many random games
	starting from that legal move where each player plays random moves until the game is over.
	monteCarloAI will keep track of which first_move lead to the most wins and play that move
	'''

	def play(self, env: connect4, move_dict: dict) -> None:

		random.seed(self.seed)

		# Create a deepcopy of the environment for simulation
		# The original env should not be modified by the AI's internal simulations.
		sim_env = deepcopy(env)
		sim_env.visualize = False # No need to visualize simulations

		# Find legal moves
		possible = sim_env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)

		if not indices: # If no legal moves, return a default/invalid move
			move_dict['move'] = 0
			return

		# Init fitness trackers to track which first_move lead to the most wins
		# Size 7 for 7 columns in Connect 4
		vs = np.zeros(sim_env.shape[1])

		counter = 0

		# Number of simulations to try and run before reaching time limit
		num_sims = 1001 # This is a target, actual number might be less due to time limits.

		save_increment = 50

		# Simulate
		while counter < num_sims: # Loop until target simulations or time limit (handled externally)

			# Pick a random first_move from available legal moves
			first_move = random.choice(indices)

			# Create a fresh environment for each simulation starting from the chosen first_move
			current_sim_env = deepcopy(sim_env)
			
			# Play the first move of the simulation
			# Ensure the move is valid before simulating
			if current_sim_env.topPosition[first_move] >= 0:
				current_sim_env.board[current_sim_env.topPosition[first_move]][first_move] = self.position
				current_sim_env.topPosition[first_move] -= 1
				current_sim_env.history[self.position-1].append(first_move) # Track in history for gameOver check
				
				# Play a random game until the game ends
				turnout = self.playRandomGame(current_sim_env, 3 - self.position) # Opponent plays next

				# Track who won the random game
				if turnout == self.position:
					vs[first_move] += 1
				elif turnout != 0: # Opponent won
					vs[first_move] -= 1
				
				counter += 1 # Increment counter only if a valid simulation was performed

			# Every save_increment games, record the best move so far
			# (in case the time limit gets reach before while loop exits)
			if counter % save_increment == 0 and counter > 0: # Ensure counter is not 0 for modulo
				# Best move is the first_move that accumulated the most random wins
				# Handle cases where all scores are 0 (e.g., if no wins yet)
				if np.max(vs) == np.min(vs) and np.max(vs) == 0:
					move_dict['move'] = random.choice(indices) # Pick a random move if all scores are zero
				else:
					# To break ties consistently, select the first occurrence of the max value
					best_moves = np.where(vs == np.max(vs))[0]
					move_dict['move'] = random.choice(best_moves) # Pick randomly among best moves
		
		# Final best move selection
		if np.max(vs) == np.min(vs) and np.max(vs) == 0:
			move_dict['move'] = random.choice(indices) # If all scores are still zero after all simulations
		else:
			best_moves = np.where(vs == np.max(vs))[0]
			move_dict['move'] = random.choice(best_moves) # Pick randomly among best moves


	def playRandomGame(self, env: connect4, current_player: int):
		'''
		Play a game from the current game state of env where each player
		plays random moves until the game it over
		Return which player won the game
		'''
		switch = {1:2,2:1}
		player = current_player

		# Play until game is over
		while True:
			# Calculate possible moves
			possible = env.topPosition >= 0
			indices = []
			for i, p in enumerate(possible):
				if p: indices.append(i)
			
			if not indices: # If no legal moves, game is a tie (board full)
				return 0

			# Select random legal move
			move = random.choice(indices)

			# Simulate move (using env's method for consistency)
			row = env.topPosition[move] # Get the row where the piece will land
			env.board[row][move] = player
			env.topPosition[move] -= 1
			env.history[player-1].append(move) # Add to history for win check

			# Check if the game is over after this move
			# Need to pass the row and column of the *last* move for efficient check
			# The row where the piece was just dropped is `row`
			if env.gameOver(move, player):
				if env.is_winner:
					return player # The player who just moved won
				else:
					return 0 # It's a tie
			
			player = switch[player] # switch which player is playing

	# The simulateMove method defined in montecarlo.py is effectively what's done inline in playRandomGame now.
	# If this was intended as a utility, it should modify a passed board/topPosition, not self.env.
	# The current usage in `playRandomGame` directly manipulates `env.board` and `env.topPosition`
	# which is correct because `env` there is a deepcopy.
	# Keeping this here but it's not strictly used anymore if `playRandomGame` is self-contained.
	def simulateMove(self, env: connect4, move: int, player: int):
		'''
		Play the move on the simulation environment
		'''
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		env.history[player-1].append(move) # Use player-1 for history index