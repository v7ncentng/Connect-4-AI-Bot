import React, { useState, useEffect } from 'react';

const ROWS = 6;
const COLS = 7;

export default function Connect4Board() {
  const [board, setBoard] = useState(Array(ROWS).fill(null).map(() => Array(COLS).fill(null)));
  const [playerTurn, setPlayerTurn] = useState(true);

  const handleClick = async (col) => {
    if (!playerTurn) return;
    const res = await fetch('http://localhost:5000/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ column: col })
    });
    const data = await res.json();
    setBoard(data.board);
    setPlayerTurn(false);
  };

  useEffect(() => {
    if (!playerTurn) {
      const getAIMove = async () => {
        const res = await fetch('http://localhost:5000/ai-move');
        const data = await res.json();
        const res2 = await fetch('http://localhost:5000/move', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ column: data.move })
        });
        const updated = await res2.json();
        setBoard(updated.board);
        setPlayerTurn(true);
      };
      getAIMove();
    }
  }, [playerTurn]);

  return (
    <div className="grid grid-cols-7 gap-1 max-w-xl mx-auto mt-10">
      {board.map((row, rowIndex) =>
        row.map((cell, colIndex) => (
          <div
            key={`${rowIndex}-${colIndex}`}
            onClick={() => handleClick(colIndex)}
            className="w-14 h-14 bg-blue-400 border rounded-full flex items-center justify-center cursor-pointer hover:bg-blue-500"
          >
            <div className={`w-10 h-10 rounded-full ${cell === 'X' ? 'bg-red-500' : cell === 'O' ? 'bg-yellow-400' : 'bg-white'}`} />
          </div>
        ))
      )}
    </div>
  );
}

