class Reversi:
    def __init__(self):
        self.size = 8
        self.symbols = {'black': '⚫', 'white': '⚪', None: '&nbsp;&nbsp;&nbsp;'}
        self.img_black = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26ab.svg'
        self.img_white = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26aa.svg'
        self.directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        self.issue_number = 2

    def set_issue_number(self, num):
        self.issue_number = num

    def create_board(self):
        board = [[None for _ in range(self.size)] for _ in range(self.size)]
        board[3][3] = board[4][4] = 'white'
        board[3][4] = board[4][3] = 'black'
        return board

    def place(self, state, position, player):
        """Place a piece on the board, flipping opponent pieces as per Reversi rules."""
        if not state['board']:
            state['board'] = self.create_board()
            state['turn'] = 'black'
            state['moves'] = []

        if len(position) != 2:
            return {'success': False, 'message': 'Invalid format. Use A1-H8'}

        col = ord(position[0]) - ord('A')
        row = int(position[1]) - 1

        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return {'success': False, 'message': 'Position out of bounds'}

        flips = self.get_flips(state['board'], row, col, state['turn'])
        if not flips:
            return {'success': False, 'message': 'Invalid placement. No pieces to flip.'}

        current_color = state['turn']
        state['board'][row][col] = current_color
        for fr, fc in flips:
            state['board'][fr][fc] = current_color

        state['moves'].append({'player': player, 'position': position, 'color': current_color})

        next_turn = 'white' if current_color == 'black' else 'black'
        if not self.has_valid_moves(state['board'], next_turn):
            if not self.has_valid_moves(state['board'], current_color):
                winner = self.get_winner(state['board'])
                msg = f'Game over! {winner} wins. Last piece placed by @{player}'
                state['board'] = None
                return {'success': True, 'message': msg}
            # skip next turn
            next_turn = current_color

        state['turn'] = next_turn
        return {'success': True, 'message': f'{self.symbols[current_color]} placed at {position} by @{player}. Flipped {len(flips)}. Next: {self.symbols[state["turn"]]}'}

    # keep make_move as alias for compatibility with game.py
    def make_move(self, state, move, player):
        return self.place(state, move, player)

    def get_flips(self, board, row, col, color):
        if board[row][col] is not None:
            return []
        opponent = 'white' if color == 'black' else 'black'
        flips = []
        for dr, dc in self.directions:
            temp = []
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size:
                if board[r][c] == opponent:
                    temp.append((r, c))
                elif board[r][c] == color:
                    flips.extend(temp)
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
        if black > white: return '⚫ Black'
        if white > black: return '⚪ White'
        return 'Draw'

    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        board = state['board'] if state['board'] else self.create_board()
        is_active = state['board'] is not None
        turn = state.get('turn', 'black')

        valid_moves = set()
        if is_active:
            for r in range(self.size):
                for c in range(self.size):
                    if self.get_flips(board, r, c, turn):
                        valid_moves.add(f"{chr(65+c)}{r+1}")
        else:
            for r in range(self.size):
                for c in range(self.size):
                    if self.get_flips(board, r, c, 'black'):
                        valid_moves.add(f"{chr(65+c)}{r+1}")

        if is_active:
            md = f"\n**Turn:** {self.symbols[turn]} | "
            black = sum(row.count('black') for row in board)
            white = sum(row.count('white') for row in board)
            md += f"⚫ {black} – ⚪ {white}\n\n"
        else:
            md = "\n"

        md += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n"
        md += "|---|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-:|\n"

        for i in range(self.size):
            md += f"| **{i+1}** | "
            for j in range(self.size):
                cell = board[i][j]
                position = f"{chr(65+j)}{i+1}"

                if cell == 'black':
                    md += f"<img src=\"{self.img_black}\" width=36px>"
                elif cell == 'white':
                    md += f"<img src=\"{self.img_white}\" width=36px>"
                elif position in valid_moves:
                    title = f"Reversi:+Put+{position}"
                    body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
                    link = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={body}"
                    md += f"[{self.symbols[None]}]({link})"
                else:
                    md += self.symbols[None]
                md += " | "
            md += f"**{i+1}** |\n"

        md += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n"

        if not is_active:
            md += "\nClick any highlighted square to start! (Black goes first)\n"
        else:
            links = []
            for p in sorted(valid_moves):
                title = f"Reversi:+Put+{p}"
                body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
                link = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={body}"
                links.append(f"[{p}]({link})")
            md += "\n" + " · ".join(links) + "\n"

            if state['moves']:
                md += "\n<details>\n  <summary>Last placements</summary>\n\n"
                md += "| Position | Player |\n| :------: | :----- |\n"
                for m in state['moves'][-5:]:
                    md += f"| `{m['position']}` ({self.symbols[m['color']]}) | [@{m['player']}](https://github.com/{m['player']}) |\n"
                md += "\n</details>\n"

        return md
