class Reversi:
    def __init__(self):
        self.size = 8
        self.symbols = {'black': '⚫', 'white': '⚪', None: '🟩'}
        # Use emoji SVGs for clean rendering
        self.img_black = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26ab.svg'
        self.img_white = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26aa.svg'
        self.img_blank = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="40" height="40"%3E%3Crect width="40" height="40" fill="%2338a169" rx="3"/%3E%3C/svg%3E'
        self.directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        self.issue_number = 2
    
    def set_issue_number(self, num):
        self.issue_number = num
    
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
    
    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        if not state['board']:
            return "*No active game.* [**Start Game →**](https://github.com/{}/{}/issues/{}/comments/new?body=start%20reversi)".format(owner, repo, self.issue_number)
        
        board = state['board']
        md = "\n**It's your turn!** Place a <!-- BEGIN TURN -->" + self.symbols[state['turn']] + "<!-- END TURN --> disc.\n\n"
        
        # Get valid moves for highlighting
        valid_moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.get_flips(board, r, c, state['turn']):
                    valid_moves.append(f"{chr(65+c)}{r+1}")
        
        # marcizhu-style board
        md += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n"
        md += "|---|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-:|\n"
        
        for i in range(self.size):
            md += f"| **{i+1}** | "
            for j in range(self.size):
                cell = board[i][j]
                position = f"{chr(65+j)}{i+1}"
                
                if cell is None and position in valid_moves:
                    # Valid move - clickable
                    link = f"https://github.com/{owner}/{repo}/issues/{self.issue_number}/comments/new?body={position}"
                    md += f"[<img src=\"{self.img_blank}\" width=40px>]({link})"
                elif cell == 'black':
                    md += f"<img src=\"{self.img_black}\" width=40px>"
                elif cell == 'white':
                    md += f"<img src=\"{self.img_white}\" width=40px>"
                else:
                    # Empty but not valid move
                    md += f"<img src=\"{self.img_blank}\" width=40px>"
                
                md += " | "
            
            md += f"**{i+1}** |\n"
        
        md += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n\n"
        
        # Score and valid moves
        black = sum(row.count('black') for row in board)
        white = sum(row.count('white') for row in board)
        md += f"**Score:** ⚫ {black} - ⚪ {white}\n\n"
        
        if valid_moves:
            md += "**Valid moves (click to play):** "
            links = [f"[{pos}](https://github.com/{owner}/{repo}/issues/{self.issue_number}/comments/new?body={pos})" for pos in valid_moves[:8]]  # Show first 8
            md += ", ".join(links)
            if len(valid_moves) > 8:
                md += f" (+{len(valid_moves)-8} more)"
            md += "\n\n"
        
        # Last moves
        if state['moves']:
            md += "<details>\n  <summary>📊 Last 3 moves</summary>\n\n"
            md += "| Move | Player | Flips |\n"
            md += "| :--: | :----- | :---: |\n"
            for m in state['moves'][-3:]:
                md += f"| `{m['move']}` ({self.symbols[m['color']]}) | [@{m['player']}](https://github.com/{m['player']}) | - |\n"
            md += "\n</details>\n"
        
        return md
