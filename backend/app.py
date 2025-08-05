# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from connect4 import connect4
# from players import alphaBetaAI, randomAI, humanGUI, humanConsole # These are player classes
from players import humanGUI, alphaBetaAI # Import specific players for the app
# from montecarlo import monteCarloAI # Not used in current app.py logic

app = Flask(__name__)
CORS(app)

# Initialize the game. By default, humanGUI plays against alphaBetaAI.
# The connect4 constructor expects player objects, not classes.
# We also need to manage turns for the API calls.
# Let's create a game instance that will be reused.
# The `connect4` object needs player instances with their positions.

# Initialize players for the app.
# Player 1 is humanGUI, Player 2 is alphaBetaAI.
# These will persist across API calls for a single game.
player1_app = humanGUI(1) 
player2_app = alphaBetaAI(2) 

game = connect4(player1=player1_app, player2=player2_app, visualize=False) # No GUI for Flask app

@app.route('/move', methods=['POST'])
def move():
    global game # Declare game as global to modify the shared instance
    col = request.json['column']
    
    # In the Flask app, we expect the human to make a move (player1_app)
    # The `play_move` method in `connect4` might need to be adjusted
    # or we need to simulate the turn-taking more explicitly here.
    
    # For now, let's assume 'move' endpoint is for the current `game.turnPlayer`
    # or that the client explicitly sends whose move it is.
    # Given the `app.js` logic, it sends the human's move (player 1).

    # Make sure it's the human's turn (Player 1)
    if game.turnPlayer.position == 1:
        # Simulate player1's move in the game
        # We don't call game.play() here as it runs the whole game loop.
        # Instead, we directly apply the move.
        row_to_play = game.topPosition[col]
        if row_to_play >= 0:
            game.board[row_to_play][col] = game.turnPlayer.position
            game.topPosition[col] -= 1
            game.history[game.turnPlayer.position-1].append(col)
            
            # Check for win/tie after human move
            if game.gameOver(col, game.turnPlayer.position):
                # Game is over. Need to communicate this back.
                winner = game.turnPlayer.position if game.is_winner else 0
                return jsonify({'board': game.board.tolist(), 'winner': winner, 'game_over': True})
            
            game.turnPlayer = game.turnPlayer.opponent # Switch to AI's turn
            return jsonify({'board': game.board.tolist(), 'game_over': False})
        else:
            return jsonify({'error': 'Column is full or invalid'}), 400
    else:
        return jsonify({'error': 'Not player 1\'s turn'}), 400


@app.route('/ai-move', methods=['GET'])
def ai_move():
    global game
    # Ensure it's the AI's turn (Player 2)
    if game.turnPlayer.position == 2:
        move_dict = {"move": -1}
        # Have the AI (player2_app) play its move
        game.player2.play(game.getEnv(), move_dict) # Pass a copy of environment
        ai_col = move_dict["move"]

        # Apply AI's move to the actual game board
        if game.topPosition[ai_col] >= 0:
            game.board[game.topPosition[ai_col]][ai_col] = game.turnPlayer.position
            game.topPosition[ai_col] -= 1
            game.history[game.turnPlayer.position-1].append(ai_col)

            # Check for win/tie after AI move
            if game.gameOver(ai_col, game.turnPlayer.position):
                winner = game.turnPlayer.position if game.is_winner else 0
                return jsonify({'move': int(ai_col), 'board': game.board.tolist(), 'winner': winner, 'game_over': True})

            game.turnPlayer = game.turnPlayer.opponent # Switch back to Human's turn
            return jsonify({'move': int(ai_col), 'board': game.board.tolist(), 'game_over': False})
        else:
            return jsonify({'error': 'AI chose an invalid column (should not happen in correct AI)'}), 500
    else:
        return jsonify({'error': 'Not AI\'s turn'}), 400

if __name__ == '__main__':
    app.run(debug=True)