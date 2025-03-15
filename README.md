# Connect-4-AI-Bot
Connect 4 AI Bot that implements Alpha-Beta Pruning to calculate the most optimal move. 

For the bot to run, you need to install numpy and pygame, using the following commands on your terminal. pip install numpy, pip install pygame (pip3 on Mac)



Pygame code used with permission from Keith Galli.
Refer to Keith Galli's Connect 4 Python for licensing. https://github.com/KeithGalli/Connect4-Python

Different commands available to use: 
-p1 -> Agent who will be acting as player 1. Name of agent eg alphaBetaAI  default type: HumanGUI ##
-p2 -> Agent who will be acting as player 2.  ##
-seed -> Seed for AI’s with stochastic elements ##
-w -> Rows of gameboard (default: 6)
-l -> Columns of gameboard (default: 7)
-visualize (Bool) -> Bool to use or not use GUI
-verbose (Bool) -> Sends move-by-move game history to shell
-limit_players (String) -> Which agents should have time limits. Useful if you want to play an AI but don’t want to have the same time limit. In the format “x,y” where x and y are players. Values that are not 1 or 2 can be used in place of 1 or 2 if the player should not be limited eg. -limit_players 1, 2
-time_limit -> Time limit for each player. No effect if a player is not limited. In the format “x,y” where x and y are floating point numbers.
-print_time_logs -> Prints information about how much time each player’s move takes, and if algorithms are being terminated early






