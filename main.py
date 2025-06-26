class Board:
    def __init__(self, height: int = 6, width: int = 7, win: int = 4):
        if height < win or width < win:
            raise Exception("The number of tokens in a row required for victory "
                            "must not exceed either dimension of the board.")

        self.height = height
        self.width = width
        self.win = win
        self.board = [["." for j in range(width)] for i in range(height)]
        self.row_indices = [height - 1 for i in range(width)]  # Start at bottom row
        self.history = []
        self.player = 1

    def copy(self):
        """Create a deep copy of the board for minimax algorithm"""
        new_board = Board(self.height, self.width, self.win)
        new_board.board = [[self.board[i][j] for j in range(self.width)] for i in range(self.height)]
        new_board.row_indices = self.row_indices.copy()
        new_board.player = self.player
        return new_board

    def is_valid_move(self, c):
        """Check if a move in column c is valid"""
        return 0 <= c < self.width and self.row_indices[c] >= 0

    def get_valid_moves(self):
        """Get all valid column moves"""
        return [c for c in range(self.width) if self.is_valid_move(c)]

    def check_win(self, r, c, dr, dc):
        """Check if there's a win starting from position (r,c) in direction (dr,dc)"""
        token = self.board[r][c]
        if token == ".":
            return False

        count = 1  # Count the current token

        # Check in positive direction
        nr, nc = r + dr, c + dc
        while (0 <= nr < self.height and 0 <= nc < self.width and
               self.board[nr][nc] == token):
            count += 1
            nr += dr
            nc += dc

        # Check in negative direction
        nr, nc = r - dr, c - dc
        while (0 <= nr < self.height and 0 <= nc < self.width and
               self.board[nr][nc] == token):
            count += 1
            nr -= dr
            nc -= dc

        return count >= self.win

    def check_winner(self, r, c):
        """Check if the last move at (r,c) resulted in a win"""
        # Check all four directions: horizontal, vertical, diagonal
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            if self.check_win(r, c, dr, dc):
                return self.board[r][c]

        return None

    def is_board_full(self):
        """Check if the board is full (tie game)"""
        return all(self.row_indices[c] < 0 for c in range(self.width))

    def make_move(self, c):
        """Make a move in column c. Returns winner if game ends, None otherwise."""
        if not self.is_valid_move(c):
            return None

        # Save current state for undo
        self.history.append({
            'board': [[self.board[i][j] for j in range(self.width)] for i in range(self.height)],
            'row_indices': self.row_indices.copy(),
            'player': self.player
        })

        # Make the move
        r = self.row_indices[c]
        token = "+" if self.player == 1 else "-"
        self.board[r][c] = token
        self.row_indices[c] -= 1  # Move up (decrease index)

        # Check for winner
        winner = self.check_winner(r, c)
        if winner:
            return 1 if winner == "+" else -1

        # Check for tie
        if self.is_board_full():
            return 0

        # Switch player
        self.player *= -1
        return None

    def undo_move(self):
        """Undo the last move"""
        if not self.history:
            return False

        last_state = self.history.pop()
        self.board = last_state['board']
        self.row_indices = last_state['row_indices']
        self.player = last_state['player']
        return True

    def reset(self):
        """Reset the board to initial state"""
        self.board = [["." for j in range(self.width)] for i in range(self.height)]
        self.row_indices = [self.height - 1 for i in range(self.width)]
        self.history = []
        self.player = 1

    def display(self):
        """Display the current board state"""
        print("\n" + " ".join(str(i) for i in range(self.width)))
        print("=" * (self.width * 2 - 1))
        for row in self.board:
            print(" ".join(row))
        print("=" * (self.width * 2 - 1))
        print("Current player:", "+" if self.player == 1 else "-")


class ConnectFourSolver:
    def __init__(self, board):
        self.board = board
        self.max_depth = 8  # Limit depth for performance

    def minimax(self, board, depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
        """Minimax algorithm with alpha-beta pruning"""
        # Check if game is over
        valid_moves = board.get_valid_moves()
        if not valid_moves or depth == 0:
            return self.evaluate_board(board), None

        # Check if last move resulted in a win
        if depth < self.max_depth:  # Only check if we made a move
            if board.is_board_full():
                return 0, None

        best_move = None

        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                board_copy = board.copy()
                result = board_copy.make_move(move)

                if result is not None:  # Game ended
                    eval_score = result
                else:
                    eval_score, _ = self.minimax(board_copy, depth - 1, False, alpha, beta)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning

            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                board_copy = board.copy()
                result = board_copy.make_move(move)

                if result is not None:  # Game ended
                    eval_score = result
                else:
                    eval_score, _ = self.minimax(board_copy, depth - 1, True, alpha, beta)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning

            return min_eval, best_move

    def evaluate_board(self, board):
        """Simple board evaluation function"""
        # Count potential wins for each player
        score = 0

        # Check all positions for potential wins
        for r in range(board.height):
            for c in range(board.width):
                if board.board[r][c] != ".":
                    # Add points based on how many in a row this position contributes to
                    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                    for dr, dc in directions:
                        line_score = self.evaluate_line(board, r, c, dr, dc)
                        if board.board[r][c] == "+":
                            score += line_score
                        else:
                            score -= line_score

        return score

    def evaluate_line(self, board, r, c, dr, dc):
        """Evaluate a line starting from (r,c) in direction (dr,dc)"""
        token = board.board[r][c]
        count = 0
        empty = 0

        # Count in positive direction
        nr, nc = r, c
        for _ in range(board.win):
            if 0 <= nr < board.height and 0 <= nc < board.width:
                if board.board[nr][nc] == token:
                    count += 1
                elif board.board[nr][nc] == ".":
                    empty += 1
                else:
                    return 0  # Blocked by opponent
            else:
                return 0  # Out of bounds
            nr += dr
            nc += dc

        if count + empty >= board.win:
            return count ** 2
        return 0

    def get_best_move(self):
        """Get the best move using minimax algorithm"""
        _, best_move = self.minimax(self.board, self.max_depth, self.board.player == 1)
        return best_move

    def play_again(self):
        """Ask if user wants to play again"""
        while True:
            choice = input("\nWould you like to play again? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")

    def play_game(self, solver):
        """Play a single game"""
        while True:
            self.board.display()

            # Check if game is over
            if self.board.is_board_full():
                print("Game Over! It's a tie!")
                return True  # Game completed

            print(f"\nPlayer {'+' if self.board.player == 1 else '-'}'s turn")
            print("Options:")
            print("1. Make a move (enter column number)")
            print("2. Let computer make optimal move (enter 'c')")
            print("3. Undo last move (enter 'u')")
            print("4. Restart game (enter 'r')")
            print("5. Quit (enter 'q')")

            choice = input("Your choice: ").strip().lower()

            if choice == 'q':
                return False  # User wants to quit
            elif choice == 'r':
                self.board.reset()
                print("Game restarted!")
                continue
            elif choice == 'u':
                if self.board.undo_move():
                    print("Move undone!")
                else:
                    print("No moves to undo!")
                continue
            elif choice == 'c':
                print("Computer is thinking...")
                best_move = solver.get_best_move()
                if best_move is not None:
                    result = self.board.make_move(best_move)
                    print(f"Computer played column {best_move}")
                    if result is not None:
                        self.board.display()
                        if result == 1:
                            print("Player + wins!")
                        elif result == -1:
                            print("Player - wins!")
                        else:
                            print("It's a tie!")
                        return True  # Game completed
                else:
                    print("No valid moves available!")
            else:
                try:
                    col = int(choice)
                    if self.board.is_valid_move(col):
                        result = self.board.make_move(col)
                        if result is not None:
                            self.board.display()
                            if result == 1:
                                print("Player + wins!")
                            elif result == -1:
                                print("Player - wins!")
                            else:
                                print("It's a tie!")
                            return True  # Game completed
                    else:
                        print("Invalid move! Column is full or out of range.")
                except ValueError:
                    print("Invalid input! Please enter a valid option.")


def main():
    print("Welcome to Connect Four Solver!")

    while True:
        # Get board dimensions
        height, width, win = 6, 7, 4
        while True:
            try:
                height = int(input("Enter board height (default 6): ") or "6")
                width = int(input("Enter board width (default 7): ") or "7")
                win = int(input("Enter number of tokens needed to win (default 4): ") or "4")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Please try again.")

        try:
            board = Board(height, width, win)
            solver = ConnectFourSolver(board)

            # Play the game
            game_completed = solver.play_game(solver)

            if not game_completed:
                print("Thanks for playing!")
                break

            # Ask if they want to play again
            if not solver.play_again():
                print("Thanks for playing!")
                break

        except Exception as e:
            print(f"Error creating board: {e}")
            print("Please try again with different settings.")


if __name__ == "__main__":
    main()
