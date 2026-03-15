class Reversi:
    def __init__(self):
        self.size = 8
        self.symbols = {'black': '⚫', 'white': '⚪', None: '🟩'}
        self.directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    
    def create_board(self):
        board = [[None for _ in range(self.size)] for _ in range(self.size)]
        # Initial setup
        board[3][3] = board[4][4] = 'white'
        board[3][4] = board[4][3] = 'black'
        return board
    
    def make_move(self, state, move, player):
        if move == 'start':
            state['board'] = self.create_board()
            state['turn'] = 'black'
            state['moves'] = []
            return {'success': True, 'message': f"🎮 New Reversi game started by @{player}! Black goes first."}
        
        if not state['board']:
            return {'success': False, 'message': 'No active game. Start with "start reversi"'}
        
        # Parse move
        if len(move) != 2:
            return {'success': False, 'message': 'Invalid format. Use A1-H8'}
        
        col = ord(move[0]) - ord('A')
        row = int(move[1]) - 1
        
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return {'success': False, 'message': 'Position out of bounds'}
        
        # Check if valid move
        flips = self.get_flips(state['board'], row, col, state['turn'])
        if not flips:
            return {'success': False, 'message': 'Invalid move. No pieces to flip.'}
        
        # Make move
        state['board'][row][col] = state['turn']
        for fr, fc in flips:
            state['board'][fr][fc] = state['turn']
        
        state['moves'].append({'player': player, 'move': move, 'color': state['turn']})
        
        # Check if game over
        next_turn = 'white' if state['turn'] == 'black' else 'black'
        if not self.has_valid_moves(state['board'], next_turn):
            if not self.has_valid_moves(state['board'], state['turn']):
                winner = self.get_winner(state['board'])
                msg = f"🎉 Game Over! {winner} wins! Last move by @{player}"
                state['board'] = None
                return {'success': True, 'message': msg}
        
        state['turn'] = next_turn
        return {'success': True, 'message': f"✅ {move} played by @{player}. Flipped {len(flips)} pieces. Next: {self.symbols[state['turn']]}"}
    
    def get_flips(self, board, row, col, color):
        if board[row][col] is not None:
            return []
        
        opponent = 'white' if color == 'black' else 'black'
        flips = []
        
        for dr, dc in self.directions:
            temp_flips = []
            r, c = row + dr, col + dc
            
            while 0 <= r < self.size and 0 <= c < self.size:
                if board[r][c] == opponent:
                    temp_flips.append((r, c))
                elif board[r][c] == color:
                    flips.extend(temp_flips)
                    break
                else:
                    break
                r, c = r + dr, c + dc
        
        return flips
    
    def has_valid_moves(self, board, color):
        for r in range(self.size):
            for c in range(self.size):
                if self.get_flips(board, r, c, color):
                    return True
        return False
    
    def get_winner(self, board):
        black = sum(row.count('black') for row in board)
        white = sum(row.count('white') for row in board)
        if black > white:
            return "⚫ Black"
        elif white > black:
            return "⚪ White"
        return "Draw"
    
    def render(self, state):
        if not state['board']:
            return "*No active game. Start with: `start reversi`*"
        
        board = state['board']
        md = "\n**Current Turn:** " + self.symbols[state['turn']] + "\n\n"
        md += "|   | A | B | C | D | E | F | G | H |\n"
        md += "|---|---|---|---|---|---|---|---|---|\n"
        
        for i, row in enumerate(board):
            md += f"| {i+1} | "
            md += " | ".join(self.symbols[cell] for cell in row)
            md += " |\n"
        
        black = sum(row.count('black') for row in board)
        white = sum(row.count('white') for row in board)
        md += f"\n**Score:** ⚫ {black} - ⚪ {white}\n"
        md += "\n**How to play:** Comment position (e.g., `D3`, `E6`)\n"
        
        return md
