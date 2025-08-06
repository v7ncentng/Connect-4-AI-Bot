# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from connect4 import connect4
from players import humanGUI, alphaBetaAI, randomAI, stupidAI, minimaxAI
from montecarlo import monteCarloAI

app = Flask(__name__)
CORS(app)

# Global game instance
game = None
current_ai_type = "alphaBetaAI"

# Available AI types
AI_TYPES = {
    "alphaBetaAI": alphaBetaAI,
    "minimaxAI": minimaxAI,
    "monteCarloAI": monteCarloAI,
    "randomAI": randomAI,
    "stupidAI": stupidAI,
    "humanGUI": humanGUI
}

def initialize_game(ai_type="alphaBetaAI"):
    """Initialize a new game instance with specified AI"""
    global game, current_ai_type
    current_ai_type = ai_type
    player1_app = humanGUI(1) 
    
    if ai_type == "humanGUI":
        # For local 2-player, both players are human
        player2_app = humanGUI(2)
    else:
        player2_class = AI_TYPES.get(ai_type, alphaBetaAI)
        player2_app = player2_class(2)
    
    game = connect4(player1=player1_app, player2=player2_app, visualize=False)
    return game

# Initialize the first game
initialize_game()

def find_winning_line(board, shape):
    """Find the winning line of 4 pieces and return their coordinates"""
    rows, cols = shape
    
    # Check horizontal
    for r in range(rows):
        for c in range(cols - 3):
            if board[r][c] != 0 and all(board[r][c + i] == board[r][c] for i in range(4)):
                return [(r, c + i) for i in range(4)]
    
    # Check vertical
    for r in range(rows - 3):
        for c in range(cols):
            if board[r][c] != 0 and all(board[r + i][c] == board[r][c] for i in range(4)):
                return [(r + i, c) for i in range(4)]
    
    # Check diagonal (positive slope)
    for r in range(rows - 3):
        for c in range(cols - 3):
            if board[r][c] != 0 and all(board[r + i][c + i] == board[r][c] for i in range(4)):
                return [(r + i, c + i) for i in range(4)]
    
    # Check diagonal (negative slope)
    for r in range(3, rows):
        for c in range(cols - 3):
            if board[r][c] != 0 and all(board[r - i][c + i] == board[r][c] for i in range(4)):
                return [(r - i, c + i) for i in range(4)]
    
    return None

def is_human_vs_human():
    """Check if the current game mode is human vs human"""
    return current_ai_type == "humanGUI"

@app.route('/set-opponent', methods=['POST'])
def set_opponent():
    """Set the AI opponent type"""
    global game
    try:
        data = request.json
        ai_type = data.get('ai_type', 'alphaBetaAI')
        
        if ai_type not in AI_TYPES:
            return jsonify({'error': f'Invalid AI type. Available: {list(AI_TYPES.keys())}'}), 400
        
        # Only allow changing opponent before any moves are made
        if game and (len(game.history[0]) > 0 or len(game.history[1]) > 0):
            return jsonify({'error': 'Cannot change opponent after game has started'}), 400
        
        initialize_game(ai_type)
        return jsonify({
            'message': f'Opponent set to {ai_type}',
            'current_opponent': ai_type,
            'board': game.board.tolist(),
            'is_human_vs_human': is_human_vs_human()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to set opponent: {str(e)}'}), 500

@app.route('/get-opponents', methods=['GET'])
def get_opponents():
    """Get list of available AI opponents"""
    opponent_info = {
        "alphaBetaAI": "Alpha-Beta AI (Smart)",
        "minimaxAI": "Minimax AI (Medium)",
        "monteCarloAI": "Monte Carlo AI (Random Simulation)",
        "randomAI": "Random AI (Easy)",
        "stupidAI": "Predictable AI (Very Easy)",
        "humanGUI": "Human Player (Local 2-Player)"
    }
    return jsonify({
        'opponents': opponent_info,
        'current': current_ai_type,
        'is_human_vs_human': is_human_vs_human()
    })

@app.route('/reset', methods=['POST'])
def reset_game():
    """Reset the game to initial state"""
    global game
    try:
        # Keep the same AI type when resetting
        initialize_game(current_ai_type)
        return jsonify({
            'board': game.board.tolist(), 
            'message': 'Game reset successfully',
            'current_player': game.turnPlayer.position,
            'current_opponent': current_ai_type,
            'is_human_vs_human': is_human_vs_human()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to reset game: {str(e)}'}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current game status"""
    global game
    if game is None:
        initialize_game()
    
    return jsonify({
        'board': game.board.tolist(),
        'current_player': game.turnPlayer.position,
        'game_over': len(game.history[0]) + len(game.history[1]) == game.shape[0] * game.shape[1],
        'valid_moves': game.get_valid_moves(),
        'is_human_vs_human': is_human_vs_human()
    })

@app.route('/move', methods=['POST'])
def move():
    global game
    
    if game is None:
        initialize_game()
    
    try:
        col = request.json['column']
        
        # Validate column
        if not (0 <= col < game.shape[1]):
            return jsonify({'error': 'Invalid column number'}), 400
        
        if game.topPosition[col] < 0:
            return jsonify({'error': 'Column is full'}), 400
        
        # For human vs human, allow both players to make moves through this endpoint
        current_player = game.turnPlayer.position
        
        # Apply the move
        row_to_play = game.topPosition[col]
        game.board[row_to_play][col] = current_player
        game.topPosition[col] -= 1
        game.history[current_player-1].append(col)
        
        # Check for win/tie after the move
        if game.gameOver(col, current_player):
            winner = current_player if game.is_winner else 0
            winning_line = find_winning_line(game.board, game.shape) if game.is_winner else None
            return jsonify({
                'board': game.board.tolist(), 
                'winner': winner, 
                'game_over': True,
                'winning_line': winning_line,
                'current_player': current_player,
                'is_human_vs_human': is_human_vs_human()
            })
        
        # Switch to the other player
        game.turnPlayer = game.turnPlayer.opponent
        
        return jsonify({
            'board': game.board.tolist(), 
            'game_over': False,
            'current_player': game.turnPlayer.position,
            'is_human_vs_human': is_human_vs_human(),
            'move_made_by': current_player
        })
        
    except KeyError:
        return jsonify({'error': 'Missing column parameter'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/ai-move', methods=['GET'])
def ai_move():
    global game
    
    if game is None:
        initialize_game()
    
    # If it's human vs human mode, don't allow AI moves
    if is_human_vs_human():
        return jsonify({'error': 'AI moves not allowed in human vs human mode'}), 400
    
    try:
        # Ensure it's the AI's turn (Player 2)
        if game.turnPlayer.position != 2:
            return jsonify({'error': 'Not AI\'s turn'}), 400

        # Get AI move
        move_dict = {"move": -1}
        game.player2.play(game.getEnv(), move_dict)
        ai_col = move_dict["move"]

        # Validate AI move
        if not (0 <= ai_col < game.shape[1]) or game.topPosition[ai_col] < 0:
            # Fallback to random valid move if AI chose invalid move
            valid_moves = game.get_valid_moves()
            if valid_moves:
                ai_col = valid_moves[0]
            else:
                return jsonify({'error': 'No valid moves available'}), 500

        # Apply AI's move
        row_to_play = game.topPosition[ai_col]
        game.board[row_to_play][ai_col] = game.turnPlayer.position
        game.topPosition[ai_col] -= 1
        game.history[game.turnPlayer.position-1].append(ai_col)

        # Check for win/tie after AI move
        if game.gameOver(ai_col, 2):  # Check if player 2 (AI) won
            winner = 2 if game.is_winner else 0
            winning_line = find_winning_line(game.board, game.shape) if game.is_winner else None
            return jsonify({
                'move': int(ai_col), 
                'board': game.board.tolist(), 
                'winner': winner, 
                'game_over': True,
                'winning_line': winning_line,
                'is_human_vs_human': False
            })

        # Switch back to human's turn
        game.turnPlayer = game.turnPlayer.opponent
        
        return jsonify({
            'move': int(ai_col), 
            'board': game.board.tolist(), 
            'game_over': False,
            'current_player': game.turnPlayer.position,
            'is_human_vs_human': False
        })
        
    except Exception as e:
        return jsonify({'error': f'AI move error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)