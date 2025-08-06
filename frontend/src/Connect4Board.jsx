import React, { useState, useEffect } from 'react';

const ROWS = 6;
const COLS = 7;

export default function Connect4Board() {
  const [board, setBoard] = useState(Array(ROWS).fill(null).map(() => Array(COLS).fill(0)));
  const [playerTurn, setPlayerTurn] = useState(true);
  const [currentPlayer, setCurrentPlayer] = useState(1); // Track which player (1 or 2) should move next
  const [gameOver, setGameOver] = useState(false);
  const [winner, setWinner] = useState(null);
  const [message, setMessage] = useState("Choose your opponent and click a column to start!");
  const [winningLine, setWinningLine] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [opponents, setOpponents] = useState({});
  const [selectedOpponent, setSelectedOpponent] = useState("alphaBetaAI");
  const [currentOpponent, setCurrentOpponent] = useState("alphaBetaAI");
  const [isHumanVsHuman, setIsHumanVsHuman] = useState(false);

  // Load available opponents when component mounts
  useEffect(() => {
    const loadOpponents = async () => {
      try {
        const res = await fetch('http://localhost:5001/get-opponents');
        const data = await res.json();
        setOpponents(data.opponents);
        setCurrentOpponent(data.current);
        setSelectedOpponent(data.current);
        setIsHumanVsHuman(data.is_human_vs_human || false);
      } catch (error) {
        console.error("Error loading opponents:", error);
      }
    };
    loadOpponents();
  }, []);

  // Function to change opponent
  const changeOpponent = async (aiType) => {
    if (gameStarted) {
      setMessage("Cannot change opponent after game has started!");
      return;
    }

    try {
      const res = await fetch('http://localhost:5001/set-opponent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ai_type: aiType })
      });

      const data = await res.json();
      if (data.error) {
        setMessage(data.error);
      } else {
        setCurrentOpponent(aiType);
        setSelectedOpponent(aiType);
        setIsHumanVsHuman(data.is_human_vs_human || false);
        
        if (data.is_human_vs_human) {
          setMessage("Local 2-Player mode! Player 1 (red) starts. Click a column!");
        } else {
          setMessage(`Now playing against ${opponents[aiType]}. Click a column to start!`);
        }
      }
    } catch (error) {
      console.error("Error changing opponent:", error);
      setMessage("Error changing opponent");
    }
  };

  // Function to reset the game state
  const resetGame = async () => {
    try {
      const res = await fetch('http://localhost:5001/reset', { method: 'POST' });
      const data = await res.json();
      
      setBoard(Array(ROWS).fill(null).map(() => Array(COLS).fill(0)));
      setPlayerTurn(true);
      setCurrentPlayer(1);
      setGameOver(false);
      setWinner(null);
      setWinningLine(null);
      setGameStarted(false);
      setIsHumanVsHuman(data.is_human_vs_human || false);
      
      if (data.is_human_vs_human) {
        setMessage("Local 2-Player mode! Player 1 (red) starts. Click a column!");
      } else {
        setMessage("Choose your opponent and click a column to start!");
      }
    } catch (error) {
      console.error("Error resetting game:", error);
      // Reset frontend state even if backend reset fails
      setBoard(Array(ROWS).fill(null).map(() => Array(COLS).fill(0)));
      setPlayerTurn(true);
      setCurrentPlayer(1);
      setGameOver(false);
      setWinner(null);
      setWinningLine(null);
      setGameStarted(false);
      setMessage("Game reset! (Backend may need manual restart)");
    }
  };

  const handleClick = async (col) => {
    console.log("Column clicked:", col);
    console.log("Current player:", currentPlayer);
    console.log("Game over:", gameOver);
    console.log("Is human vs human:", isHumanVsHuman);
    
    if (gameOver) {
      console.log("Click ignored - game over");
      return;
    }

    // For human vs human, allow both players to click
    // For human vs AI, only allow when it's player 1's turn
    if (!isHumanVsHuman && !playerTurn) {
      console.log("Click ignored - not player 1's turn in vs AI mode");
      return;
    }

    // Set game as started on first move
    if (!gameStarted) {
      setGameStarted(true);
    }

    if (isHumanVsHuman) {
      setMessage(`Player ${currentPlayer === 1 ? 2 : 1} (${currentPlayer === 1 ? 'yellow' : 'red'}), your turn!`);
    } else {
      setMessage("Making your move...");
    }

    try {
      console.log("Sending move to backend:", col);
      const res = await fetch('http://localhost:5001/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ column: col })
      });

      console.log("Response status:", res.status);

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log("Response data:", data);

      if (data.error) {
        // Handle specific game errors (like column full) without showing connection error
        if (data.error.includes("full") || data.error.includes("invalid")) {
          setMessage(data.error);
        } else {
          setMessage("❌ Game error: " + data.error);
        }
        return;
      }

      setBoard(data.board);
      setCurrentPlayer(data.current_player);

      if (data.game_over) {
        setGameOver(true);
        setWinner(data.winner);
        setWinningLine(data.winning_line);
        
        if (data.winner === 1) {
          setMessage("Player 1 (Red) Wins! 🎉");
        } else if (data.winner === 2) {
          if (isHumanVsHuman) {
            setMessage("Player 2 (Yellow) Wins! 🎉");
          } else {
            setMessage(`${opponents[currentOpponent]?.split(' ')[0] || 'AI'} Wins! 🤖`);
          }
        } else {
          setMessage("It's a Tie! 🤝");
        }
      } else {
        if (isHumanVsHuman) {
          // In human vs human, both players click, so just update the message
          const nextPlayerName = data.current_player === 1 ? "Player 1 (Red)" : "Player 2 (Yellow)";
          setMessage(`${nextPlayerName}, your turn!`);
          setPlayerTurn(true); // Always allow clicking in human vs human
        } else {
          // In human vs AI mode, switch to AI's turn
          setPlayerTurn(false);
          const opponentName = opponents[currentOpponent]?.split(' ')[0] || 'AI';
          setMessage(`${opponentName} is thinking...`);
        }
      }
    } catch (error) {
      console.error("Error making human move:", error);
      // Only show connection error for actual network/connection issues
      setMessage("❌ Cannot connect to backend. Make sure Flask server is running on localhost:5001");
    }
  };

  useEffect(() => {
    // Only fetch AI move if it's AI's turn and game is not over and NOT human vs human
    if (!playerTurn && !gameOver && !isHumanVsHuman) {
      const getAIMove = async () => {
        try {
          const res = await fetch('http://localhost:5001/ai-move');
          
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }

          const data = await res.json();

          if (data.error) {
            setMessage(data.error);
            return;
          }
          
          setBoard(data.board);
          setCurrentPlayer(data.current_player);

          if (data.game_over) {
            setGameOver(true);
            setWinner(data.winner);
            setWinningLine(data.winning_line);
            if (data.winner === 1) setMessage("You Win! 🎉");
            else if (data.winner === 2) setMessage(`${opponents[currentOpponent]?.split(' ')[0] || 'AI'} Wins! 🤖`);
            else setMessage("It's a Tie! 🤝");
          } else {
            setPlayerTurn(true);
            setMessage("It's your turn!");
          }
        } catch (error) {
          console.error("Error getting AI move:", error);
          setMessage("Error: Cannot connect to backend for AI move");
        }
      };
      const aiThinkingTimer = setTimeout(getAIMove, 500);
      return () => clearTimeout(aiThinkingTimer);
    }
  }, [playerTurn, gameOver, isHumanVsHuman]);

  // Function to check if a cell is part of the winning line
  const isWinningCell = (row, col) => {
    if (!winningLine) return false;
    return winningLine.some(([r, c]) => r === row && c === col);
  };

  // Function to determine cell color based on player number
  const getCellColor = (cellValue, row, col) => {
    const baseColor = cellValue === 1 ? 'bg-red-500' : cellValue === 2 ? 'bg-yellow-400' : 'bg-white';
    
    if (isWinningCell(row, col)) {
      return `${baseColor} ring-4 ring-white shadow-2xl`;
    }
    
    return baseColor;
  };

  // Get appropriate turn indicator
  const getTurnIndicator = () => {
    if (gameOver) return "";
    
    if (isHumanVsHuman) {
      return currentPlayer === 1 ? "🔴" : "🟡";
    } else {
      return playerTurn ? "🔴" : "🤖";
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-purple-800 p-4 text-white">
      <h1 className="text-5xl font-bold mb-4 text-white drop-shadow-lg">Connect 4</h1>
      
      {/* Opponent Selection Dropdown */}
      {!gameStarted && (
        <div className="mb-6 flex flex-col items-center">
          <label className="text-lg font-semibold mb-2">Choose Your Opponent:</label>
          <select 
            value={selectedOpponent}
            onChange={(e) => {
              setSelectedOpponent(e.target.value);
              changeOpponent(e.target.value);
            }}
            className="bg-blue-700 text-white px-4 py-2 rounded-lg border border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400 text-center min-w-64"
          >
            {Object.entries(opponents).map(([key, description]) => (
              <option key={key} value={key}>
                {description}
              </option>
            ))}
          </select>
        </div>
      )}

      {gameStarted && (
        <div className="mb-4 text-lg text-blue-200">
          {isHumanVsHuman ? (
            <>Playing: <span className="font-semibold text-white">Local 2-Player</span></>
          ) : (
            <>Playing against: <span className="font-semibold text-white">{opponents[currentOpponent]}</span></>
          )}
        </div>
      )}
      
      <div className="mb-6 text-2xl font-semibold text-center min-h-8 flex items-center gap-2">
        <span>{getTurnIndicator()}</span>
        <span>{message}</span>
      </div>

      <div className="relative">
        {/* Column click areas */}
        <div className="absolute -top-16 left-0 right-0 h-16 flex z-10">
          {Array.from({ length: COLS }).map((_, colIndex) => (
            <div
              key={`click-${colIndex}`}
              onClick={() => handleClick(colIndex)}
              className="flex-1 h-full cursor-pointer hover:bg-white hover:bg-opacity-20 rounded-t-lg transition-all duration-200 flex items-center justify-center"
              style={{ minHeight: '64px' }}
            >
              <div 
                className={`w-3 h-3 rounded-full opacity-0 hover:opacity-100 transition-opacity duration-200 ${
                  isHumanVsHuman 
                    ? (currentPlayer === 1 ? 'bg-red-500' : 'bg-yellow-400')
                    : 'bg-red-500'
                }`} 
              />
            </div>
          ))}
        </div>

        {/* Game board */}
        <div className="grid grid-cols-7 gap-2 p-4 bg-blue-600 rounded-2xl shadow-2xl border-4 border-blue-500">
          {board.map((row, rowIndex) => (
            row.map((cell, colIndex) => (
              <div
                key={`${rowIndex}-${colIndex}`}
                onClick={() => handleClick(colIndex)}
                className="w-16 h-16 bg-blue-800 rounded-full flex items-center justify-center shadow-inner cursor-pointer hover:bg-blue-700 transition-colors duration-200"
              >
                <div 
                  className={`w-12 h-12 rounded-full ${getCellColor(cell, rowIndex, colIndex)} shadow-lg transition-all duration-300 ease-out border-2 border-opacity-20 border-white`}
                />
              </div>
            ))
          ))}
        </div>
      </div>

      {gameOver && (
        <button
          onClick={resetGame}
          className="mt-8 px-8 py-4 bg-green-500 hover:bg-green-600 text-white font-bold text-xl rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105"
        >
          Play Again
        </button>
      )}

      <div className="mt-6 text-sm text-blue-200 text-center">
        <p>Click on a column to drop your piece</p>
        <p>Connect 4 pieces horizontally, vertically, or diagonally to win!</p>
        {isHumanVsHuman && (
          <p className="mt-1 font-semibold">🔴 Player 1 (Red) vs 🟡 Player 2 (Yellow)</p>
        )}
      </div>
    </div>
  );
}