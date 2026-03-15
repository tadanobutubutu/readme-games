class TicTacToe:
    def __init__(self):
        self.size = 3
        self.symbols = {'X': '❌', 'O': '⭕', None: '⬜'}
        self.issue_number = 1  # Default, will be updated from game_data
    
    def set_issue_number(self, num):
        self.issue_number = num
    
    def create_board(self):
        return [[None for _ in range(self.size)] for _ in range(self.size)]
    
    def make_move(self, state, move, player):
        if move == 'start':
            state['board'] = self.create_board()
            state['turn'] = 'X'
            state['moves'] = []
            return {'success': True, 'message': f"🎮 New Tic-Tac-Toe game started by @{player}! X goes first."}
        
        if not state['board']:
            return {'success': False, 'message': 'No active game. Start a new game with "start ttt"'}
        
        # Parse move (e.g., "A1" -> row 0, col 0)
        if len(move) != 2:
            return {'success': False, 'message': 'Invalid format. Use A1-C3 (e.g., B2)'}
        
        col = ord(move[0]) - ord('A')
        row = int(move[1]) - 1
        
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return {'success': False, 'message': 'Position out of bounds'}
        
        if state['board'][row][col] is not None:
            return {'success': False, 'message': 'Position already taken'}
        
        # Make move
        state['board'][row][col] = state['turn']
        state['moves'].append({'player': player, 'move': move, 'symbol': state['turn']})
        
        # Check win
        winner = self.check_winner(state['board'])
        if winner:
            msg = f"🎉 Game Over! {self.symbols[winner]} wins! Played by @{player}"
            state['board'] = None  # Reset for next game
            return {'success': True, 'message': msg}
        
        # Check draw
        if self.is_full(state['board']):
            msg = f"🤝 Game Over! It's a draw! Last move by @{player}"
            state['board'] = None
            return {'success': True, 'message': msg}
        
        # Switch turn
        state['turn'] = 'O' if state['turn'] == 'X' else 'X'
        return {'success': True, 'message': f"✅ Move {move} played by @{player}. Next: {self.symbols[state['turn']]}"}
    
    def check_winner(self, board):
        # Rows and columns
        for i in range(self.size):
            if board[i][0] and board[i][0] == board[i][1] == board[i][2]:
                return board[i][0]
            if board[0][i] and board[0][i] == board[1][i] == board[2][i]:
                return board[0][i]
        
        # Diagonals
        if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
            return board[0][0]
        if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
            return board[0][2]
        
        return None
    
    def is_full(self, board):
        return all(cell is not None for row in board for cell in row)
    
    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        if not state['board']:
            return "*No active game. Start with: `start ttt` or `start tictactoe`*"
        
        board = state['board']
        md = "\n**Current Turn:** " + self.symbols[state['turn']] + "\n\n"
        
        # Clickable board with emoji buttons
        md += "**🎯 Click a position to make your move:**\n\n"
        md += "<table><tr><td></td><td align='center'><b>A</b></td><td align='center'><b>B</b></td><td align='center'><b>C</b></td></tr>"
        
        for i in range(self.size):
            md += f"<tr><td align='center'><b>{i+1}</b></td>"
            for j in range(self.size):
                cell = board[i][j]
                position = f"{chr(65+j)}{i+1}"
                
                if cell is None:
                    # Empty cell - clickable
                    link = f"https://github.com/{owner}/{repo}/issues/{self.issue_number}/comments/new?body={position}"
                    md += f"<td align='center'><a href='{link}'>▫️</a></td>"
                else:
                    # Occupied cell - not clickable
                    md += f"<td align='center'>{self.symbols[cell]}</td>"
            md += "</tr>"
        
        md += "</table>\n\n"
        md += "**📝 Or comment directly:** `A1`, `B2`, `C3`, etc.\n\n"
        
        md += "**📊 Last 3 moves:**\n\n"
        
        if state['moves']:
            for m in state['moves'][-3:]:
                md += f"- {self.symbols[m['symbol']]} {m['move']} by @{m['player']}\n"
        else:
            md += "*No moves yet*\n"
        
        return md
