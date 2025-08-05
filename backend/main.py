# main.py
import argparse
from connect4 import connect4
from players import humanGUI, stupidAI, randomAI, humanConsole, minimaxAI, alphaBetaAI
from montecarlo import monteCarloAI

parser = argparse.ArgumentParser(description='Run programming assignment 2')
parser.add_argument('-w', default=6, type=int, help='Rows of game')
parser.add_argument('-l', default=7, type=int, help='Columns of game')
parser.add_argument('-p1', default='humanGUI', type=str, help='Player 1 agent. Use any of the following: [humanGUI, humanConsole, stupidAI, randomAI, monteCarloAI, minimaxAI, alphaBetaAI]')
parser.add_argument('-p2', default='humanGUI', type=str, help='Player 2 agent. Use any of the following: [humanGUI, humanConsole, stupidAI, randomAI, monteCarloAI, minimaxAI, alphaBetaAI]')
parser.add_argument('-seed', default=0, type=int, help='Seed for random algorithms')
parser.add_argument('-visualize', default='True', type=str, help='Use GUI')
parser.add_argument('-verbose', default='True', type=str, help='Print boards to shell')
parser.add_argument('-limit_players', default='1,2', type=str, help='Players to limit time for. List players as numbers eg [1,2]')
parser.add_argument('-time_limit', default='1.0,1.0', type=str, help='Time limits for each player. Must be list of 2 elements > 0. Not used if player is not listed')
parser.add_argument('-cvd_mode', default='False', type=str, help='Uses colorblind-friendly palette')
parser.add_argument('-print_time_logs', default='False', type=str, help='Print metrics about how fast each turn takes, and if time limits are being exceeded')


# Bools and argparse are not friends
bool_dict = {'True': True, 'False': False}

args = parser.parse_args()

w = args.w
l = args.l

seed = args.seed
visualize = bool_dict[args.visualize]
verbose = bool_dict[args.verbose]

# Parse limit_players as a list of integers
limit_players_str = args.limit_players.split(',')
limit_players = []
for v in limit_players_str:
    try:
        limit_players.append(int(v.strip()))
    except ValueError:
        print(f"Warning: Could not parse '{v.strip()}' as an integer for limit_players. Skipping.")
        
# Parse time_limit as a list of floats
time_limit_str = args.time_limit.split(',')
time_limit = []
for v in time_limit_str:
    try:
        time_limit.append(float(v.strip()))
    except ValueError:
        print(f"Warning: Could not parse '{v.strip()}' as a float for time_limit. Skipping.")


cvd_mode = bool_dict[args.cvd_mode]
print_time_logs = bool_dict[args.print_time_logs] # Ensure this is also converted to bool


agents = {
	'humanGUI': humanGUI, 
	'humanConsole': humanConsole, 
	'stupidAI': stupidAI, 
	'randomAI': randomAI, 
	'monteCarloAI': monteCarloAI, 
	'minimaxAI': minimaxAI, 
	'alphaBetaAI': alphaBetaAI
	}

if __name__ == '__main__':

	player1_agent_class = agents.get(args.p1)
	player2_agent_class = agents.get(args.p2)

	if player1_agent_class is None:
		print(f"Error: Player 1 agent '{args.p1}' not found. Using humanGUI as default.")
		player1_agent_class = humanGUI
	if player2_agent_class is None:
		print(f"Error: Player 2 agent '{args.p2}' not found. Using humanGUI as default.")
		player2_agent_class = humanGUI

	player1 = player1_agent_class(1, seed, cvd_mode)
	player2 = player2_agent_class(2, seed, cvd_mode)
	
	c4 = connect4(
		player1=player1, 
		player2=player2, 
		board_shape=(w,l), 
		visualize=visualize, 
		limit_players=limit_players, 
		time_limit=time_limit, 
		verbose=verbose, 
		CVDMode=cvd_mode, 
		print_time_logs=print_time_logs
	)
	c4.play()