import React, { useState, useEffect } from 'react';

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

const ROWS = 6;
const COLS = 7;

export default function Connect4Board() {
  // Initialize board with 0s (empty) to match Python backend
  const [board, setBoard] = useState(Array(ROWS).fill(null).map(() => Array(COLS).fill(0)));
  const [playerTurn, setPlayerTurn] = useState(true); // true for human (Player 1), false for AI (Player 2)
  const [gameOver, setGameOver] = useState(false);
  const [winner, setWinner] = useState(null); // null, 0 (tie), 1 (Player 1), 2 (Player 2)
  const [message, setMessage] = useState("It's your turn!");

  // Function to reset the game state
  const resetGame = async () => {
    // You'll need a /reset endpoint in your app.py to fully reset the backend game state.
    // For now, we'll just reset frontend state and alert the user they need to restart backend.
    // Ideally, uncomment the fetch('/reset') if you add it to app.py
    // await fetch('http://localhost:5000/reset', { method: 'POST' });
    setBoard(Array(ROWS).fill(null).map(() => Array(COLS).fill(0)));
    setPlayerTurn(true);
    setGameOver(false);
    setWinner(null);
    setMessage("Game reset! It's your turn!");
    // For now, you might need to manually restart the Flask app for a full backend reset.
  };


  const handleClick = async (col) => {
    if (!playerTurn || gameOver) return;

    try {
      const res = await fetch('http://localhost:5001/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ column: col })
      });

      const data = await res.json();

      if (data.error) {
        setMessage(data.error);
        return;
      }

      setBoard(data.board);

      if (data.game_over) {
        setGameOver(true);
        setWinner(data.winner);
        if (data.winner === 1) setMessage("You Win!");
        else if (data.winner === 2) setMessage("AI Wins!");
        else setMessage("It's a Tie!");
      } else {
        setPlayerTurn(false); // Switch to AI's turn
        setMessage("AI is thinking...");
      }
    } catch (error) {
      console.error("Error making human move:", error);
      setMessage("Error making move. Check console.");
    }
  };

  useEffect(() => {
    // Only fetch AI move if it's AI's turn and game is not over
    if (!playerTurn && !gameOver) {
      const getAIMove = async () => {
        try {
          const res = await fetch('http://localhost:5000/ai-move');
          const data = await res.json();

          if (data.error) {
            setMessage(data.error);
            return;
          }
          
          setBoard(data.board); // Update board with AI's move

          if (data.game_over) {
            setGameOver(true);
            setWinner(data.winner);
            if (data.winner === 1) setMessage("You Win!");
            else if (data.winner === 2) setMessage("AI Wins!");
            else setMessage("It's a Tie!");
          } else {
            setPlayerTurn(true); // Switch back to human's turn
            setMessage("It's your turn!");
          }
        } catch (error) {
          console.error("Error getting AI move:", error);
          setMessage("Error with AI move. Check console.");
        }
      };
      const aiThinkingTimer = setTimeout(getAIMove, 500); // Give a small delay for AI to 'think'
      return () => clearTimeout(aiThinkingTimer); // Cleanup timeout if component unmounts
    }
  }, [playerTurn, gameOver]); // Depend on playerTurn and gameOver states

  // Function to determine cell color based on player number
  const getCellColor = (cellValue) => {
    if (cellValue === 1) return 'bg-red-500'; // Player 1
    if (cellValue === 2) return 'bg-yellow-400'; // Player 2
    return 'bg-white'; // Empty
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-4xl font-bold mb-6 text-blue-800">Connect 4</h1>
      <div className="mb-4 text-xl font-semibold">
        {message}
      </div>
      <div className="grid grid-cols-7 gap-1 max-w-xl mx-auto border-4 border-blue-600 rounded-lg overflow-hidden shadow-2xl">
        {/* Render columns for clickable areas on top */}
        {!gameOver && (
            <div className="absolute top-0 left-0 right-0 h-14 flex justify-between z-10">
                {Array.from({ length: COLS }).map((_, colIndex) => (
                    <div
                        key={`top-click-${colIndex}`}
                        onClick={() => handleClick(colIndex)}
                        className="flex-1 h-full cursor-pointer hover:bg-blue-700 opacity-20" // Visual feedback on hover
                    />
                ))}
            </div>
        )}
        
        {board.map((row, rowIndex) => (
          row.map((cell, colIndex) => (
            <div
              key={`${rowIndex}-${colIndex}`}
              // Removed onClick from individual cells, moved to the top clickable layer
              className="w-14 h-14 bg-blue-400 flex items-center justify-center relative" // Use relative for piece positioning
              style={{ padding: '4px' }} // Padding to show the blue background
            >
              <div 
                className={`w-12 h-12 rounded-full ${getCellColor(cell)} transition-all duration-300 ease-out`} 
                // Position pieces from bottom up. Board data is top-down (row 0 is top).
                // So, for visualization, map row index to physical position from bottom.
                style={{
                  transform: `translateY(${((ROWS - 1 - rowIndex) * (56 + 4)) - (rowIndex * (56 + 4))}px)`, // Adjust for correct visual stacking, or simpler, let CSS grid handle it
                  // Simpler: Just rely on grid to place them. The Python board is row 0 = top, row 5 = bottom.
                  // CSS grid naturally fills top-left.
                }}
              />
            </div>
          ))
        ))}
      </div>
      {gameOver && (
        <button
          onClick={resetGame}
          className="mt-6 px-6 py-3 bg-green-500 text-white font-bold rounded-lg shadow-md hover:bg-green-600 transition-colors"
        >
          Play Again
        </button>
      )}
    </div>
  );
}