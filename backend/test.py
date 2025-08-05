# test.py
from connect4 import connect4
from players import randomAI, alphaBetaAI
from montecarlo import monteCarloAI


board_shape = (6,7)
visualize = False 
verbose = False
limit_players = (1,2) # This should be a list for connect4 init: [1,2]
time_limit = (3.0, 3.0) # This should be a list for connect4 init: [3.0, 3.0]
cvd_mode = False

def play_game(p1, p2):
    '''
    p1 - connect4Player - player who will play first 
    p2 - connect4Player - player who will play second 

    returns winner
    '''

    c4 = connect4(
        player1 = p1, 
        player2 = p2, 
        board_shape = board_shape,
        visualize = visualize,
        limit_players = list(limit_players), # Convert tuple to list
        time_limit = list(time_limit),       # Convert tuple to list
        verbose = verbose,
        save = False,
        CVDMode = False,
        print_time_logs= True
        ) 

    winner = c4.play()

    return winner == 0, winner == 1, winner == 2

w = 0 
t = 0 
l = 0

for competitor, n_trials in zip([randomAI, monteCarloAI], [5, 5]): 
    print(f"\n--- Testing against {competitor.__name__} ---")
    for i in range(n_trials):
        print(f"\nGame {i+1} against {competitor.__name__}")
        
        # You play first (alphaBetaAI is player 1)
        # Ensure new instances for each game to reset internal states (history, etc.)
        p1_instance_1 = alphaBetaAI(1, i) 
        p2_instance_1 = competitor(2, i)
        t1, w1, l1 = play_game(p1_instance_1, p2_instance_1)
        
        # You play second (alphaBetaAI is player 2)
        p1_instance_2 = competitor(1, i)
        p2_instance_2 = alphaBetaAI(2, i)
        t2, l2, w2 = play_game(p1_instance_2, p2_instance_2) # Note: w2, l2 are swapped here in original logic
        # It should be t2, w2_alpha, l2_alpha if w2 is alpha's win, but original had l2, w2.
        # Let's adjust to match what `play_game` returns for alphaBetaAI (player 2 in this case)
        # play_game returns (is_tie, is_p1_win, is_p2_win)
        # So for (competitor(1, i), alphaBetaAI(2, i)), results are:
        # t2: tie, l2: competitor win (alphaBetaAI loss), w2: alphaBetaAI win
        
        # Track metrics
        w += w1 + w2 # alphaBetaAI wins
        t += t1 + t2 # ties
        l += l1 + l2 # alphaBetaAI losses

        print(f"Competitor: {competitor.__name__} Test: {i} | AlphaBetaAI Wins: {w1 + w2} | Ties: {t1 + t2} | AlphaBetaAI Losses: {l1 + l2}")

# Print Metrics
# wins are worth 1pt and ties are worth 0.5pts
points = w + t * 0.5

print(f"\n--- Final AlphaBetaAI Performance Metrics ---")
print(f"Wins: {w} | Ties: {t} | Losses: {l} | Points: {points}/20") # Total 10 games (5*2)