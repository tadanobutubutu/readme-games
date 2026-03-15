class TicTacToe:
    def __init__(self):
        self.size = 3
        self.symbols = {'X': '❌', 'O': '⭕', None: '⬜'}
        # Use emoji data URIs for clean rendering
        self.img_x = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/274c.svg'
        self.img_o = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/2b55.svg'
        self.img_blank = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="50" height="50"%3E%3Crect width="50" height="50" fill="%23f0f0f0" rx="5"/%3E%3C/svg%3E'
        self.issue_number = 1
    
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
            state['board'] = None
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
            return "*No active game.* [**Start Game →**](https://github.com/{}/{}/issues/{}/comments/new?body=start%20ttt)".format(owner, repo, self.issue_number)
        
        board = state['board']
        md = "\n**It's your turn!** Move a <!-- BEGIN TURN -->" + self.symbols[state['turn']] + "<!-- END TURN --> piece.\n\n"
        
        # marcizhu-style board with images
        md += "|   | **A** | **B** | **C** |   |\n"
        md += "|---|:-----:|:-----:|:-----:|:-:|\n"
        
        for i in range(self.size):
            md += f"| **{i+1}** | "
            for j in range(self.size):
                cell = board[i][j]
                position = f"{chr(65+j)}{i+1}"
                
                if cell is None:
                    # Empty cell - clickable image
                    link = f"https://github.com/{owner}/{repo}/issues/{self.issue_number}/comments/new?body={position}"
                    md += f"[<img src=\"{self.img_blank}\" width=50px>]({link})"
                elif cell == 'X':
                    # X piece
                    md += f"<img src=\"{self.img_x}\" width=50px>"
                else:
                    # O piece
                    md += f"<img src=\"{self.img_o}\" width=50px>"
                
                md += " | "
            
            md += f"**{i+1}** |\n"
        
        md += "|   | **A** | **B** | **C** |   |\n\n"
        
        # Show available moves like marcizhu
        empty_positions = []
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] is None:
                    empty_positions.append(f"{chr(65+j)}{i+1}")
        
        if empty_positions:
            md += "**Click any empty square to play!** Or choose from: "
            links = [f"[{pos}](https://github.com/{owner}/{repo}/issues/{self.issue_number}/comments/new?body={pos})" for pos in empty_positions]
            md += ", ".join(links) + "\n\n"
        
        # Last moves
        if state['moves']:
            md += "<details>\n  <summary>📊 Last 3 moves</summary>\n\n"
            md += "| Move | Player |\n"
            md += "| :--: | :----- |\n"
            for m in state['moves'][-3:]:
                md += f"| `{m['move']}` ({self.symbols[m['symbol']]}) | [@{m['player']}](https://github.com/{m['player']}) |\n"
            md += "\n</details>\n"
        
        return md
