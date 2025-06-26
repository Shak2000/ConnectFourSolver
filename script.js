let gameBoard = null;
let gameOver = false;
let currentPlayer = 1;

// Initialize the game
async function initializeGame() {
    try {
        await loadBoard();
        renderBoard();
    } catch (error) {
        showError('Failed to initialize game: ' + error.message);
    }
}

// Load board state from API
async function loadBoard() {
    try {
        const response = await fetch('/get_board');
        if (!response.ok) throw new Error('Failed to load board');
        gameBoard = await response.json();
        currentPlayer = gameBoard.player;
        updateGameStatus();
    } catch (error) {
        throw error;
    }
}

// Create new board with custom dimensions
async function createNewBoard() {
    const height = parseInt(document.getElementById('height').value);
    const width = parseInt(document.getElementById('width').value);
    const win = parseInt(document.getElementById('win').value);

    if (height < win || width < win) {
        showError('The number of tokens required to win must not exceed board dimensions');
        return;
    }

    try {
        showLoading(true);
        const response = await fetch('/create_board', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ height, width, win })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create board');
        }

        gameBoard = await response.json();
        currentPlayer = gameBoard.player;
        gameOver = false;
        renderBoard();
        updateGameStatus();
        showSuccess('New game created successfully!');
    } catch (error) {
        showError('Failed to create new board: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Reset current game
async function resetGame() {
    try {
        showLoading(true);
        const response = await fetch('/reset', { method: 'POST' });
        if (!response.ok) throw new Error('Failed to reset game');

        gameBoard = await response.json();
        currentPlayer = gameBoard.player;
        gameOver = false;
        renderBoard();
        updateGameStatus();
        showSuccess('Game reset successfully!');
    } catch (error) {
        showError('Failed to reset game: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Undo last move
async function undoMove() {
    try {
        showLoading(true);
        const response = await fetch('/undo_move', { method: 'POST' });
        if (!response.ok) throw new Error('Failed to undo move');

        gameBoard = await response.json();
        currentPlayer = gameBoard.player;
        gameOver = false;
        renderBoard();
        updateGameStatus();
        showSuccess('Move undone!');
    } catch (error) {
        showError('Failed to undo move: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Make a move in specified column
async function makeMove(column) {
    if (gameOver) return;

    try {
        showLoading(true);
        const response = await fetch('/make_move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ column })
        });

        if (!response.ok) throw new Error('Invalid move');

        gameBoard = await response.json();
        currentPlayer = gameBoard.player;
        renderBoard();
        checkGameEnd();
        updateGameStatus();
    } catch (error) {
        showError('Failed to make move: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Get AI move
async function getAIMove() {
    if (gameOver) return;

    try {
        showLoading(true);
        const response = await fetch('/get_best_move');
        if (!response.ok) throw new Error('Failed to get AI move');

        const bestMove = await response.json();
        if (bestMove === null) {
            showError('No valid moves available');
            return;
        }

        await makeMove(bestMove);
    } catch (error) {
        showError('Failed to get AI move: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Render the game board
function renderBoard() {
    if (!gameBoard) return;

    const boardGrid = document.getElementById('boardGrid');
    const columnHeaders = document.getElementById('columnHeaders');

    // Set grid dimensions
    boardGrid.style.gridTemplateColumns = `repeat(${gameBoard.width}, 1fr)`;
    columnHeaders.style.gridTemplateColumns = `repeat(${gameBoard.width}, 1fr)`;

    // Render column headers
    columnHeaders.innerHTML = '';
    for (let c = 0; c < gameBoard.width; c++) {
        const header = document.createElement('button');
        header.className = 'column-header';
        header.textContent = c;
        header.onclick = () => makeMove(c);
        header.disabled = gameOver || !isValidMove(c);
        columnHeaders.appendChild(header);
    }

    // Render board cells
    boardGrid.innerHTML = '';
    for (let r = 0; r < gameBoard.height; r++) {
        for (let c = 0; c < gameBoard.width; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';

            const cellValue = gameBoard.board[r][c];
            if (cellValue === '+') {
                cell.className += ' player1';
                cell.textContent = '🔴';
            } else if (cellValue === '-') {
                cell.className += ' player2';
                cell.textContent = '🟡';
            }

            cell.onclick = () => makeMove(c);
            boardGrid.appendChild(cell);
        }
    }
}

// Check if move is valid
function isValidMove(column) {
    if (!gameBoard) return false;
    return gameBoard.row_indices[column] >= 0;
}

// Check if game has ended
function checkGameEnd() {
    if (gameBoard.game_over) {
        gameOver = true;
        return;
    }

    // Check for tie (board full)
    const isFull = gameBoard.row_indices.every(index => index < 0);
    if (isFull) {
        gameOver = true;
    }
}

// Update game status display
function updateGameStatus() {
    const statusElement = document.getElementById('gameStatus');

    if (gameOver) {
        if (gameBoard.winner === 1) {
            statusElement.className = 'game-status status-winner';
            statusElement.textContent = "🎉 Player 1 (Red) Wins!";
        } else if (gameBoard.winner === -1) {
            statusElement.className = 'game-status status-winner';
            statusElement.textContent = "🎉 Player 2 (Yellow) Wins!";
        } else {
            statusElement.className = 'game-status status-tie';
            statusElement.textContent = "Game Over - It's a Tie!";
        }
    } else {
        statusElement.className = 'game-status status-playing';
        const playerName = currentPlayer === 1 ? 'Player 1 (Red)' : 'Player 2 (Yellow)';
        statusElement.textContent = `${playerName}'s Turn - Click a column or use AI`;
    }
}

// Show loading indicator
function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    if (show) {
        loadingElement.classList.add('show');
    } else {
        loadingElement.classList.remove('show');
    }
}

// Show error message
function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

// Show success message
function showSuccess(message) {
    const successElement = document.getElementById('successMessage');
    successElement.textContent = message;
    successElement.style.display = 'block';
    setTimeout(() => {
        successElement.style.display = 'none';
    }, 3000);
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', initializeGame);
