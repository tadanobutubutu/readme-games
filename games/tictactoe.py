class TicTacToe:
    def __init__(self):
        self.size = 3
        self.symbols = {'X': '❌', 'O': '⭕', None: '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'}
        self.img_x = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/274c.svg'
        self.img_o = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/2b55.svg'
        self.issue_number = 1

    def set_issue_number(self, num):
        self.issue_number = num

    def create_board(self):
        return [[None for _ in range(self.size)] for _ in range(self.size)]

    def make_move(self, state, position, player):
        """Place a piece on the specified position. Never moves existing pieces."""

        # Initialize board if game not yet started
        if state.get('board') is None:
            state['board'] = self.create_board()
            state['turn'] = 'X'
            state['moves'] = []

        if len(position) != 2:
            return {'success': False, 'message': 'Invalid format. Use A1-C3 (e.g., B2)'}

        col = ord(position[0].upper()) - ord('A')
        row = int(position[1]) - 1

        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return {'success': False, 'message': 'Position out of bounds'}

        # Strictly reject occupied squares - no movement allowed
        if state['board'][row][col] is not None:
            return {'success': False, 'message': f'Square {position} is already occupied!'}

        current_symbol = state['turn']
        state['board'][row][col] = current_symbol
        state['moves'].append({
            'player': player,
            'position': position.upper(),
            'symbol': current_symbol
        })

        winner = self.check_winner(state['board'])
        if winner:
            state['board'] = None
            state['turn'] = 'X'
            state['moves'] = []
            return {'success': True, 'message': f'{self.symbols[winner]} wins! Game over. Placed by @{player}'}

        if self.is_full(state['board']):
            state['board'] = None
            state['turn'] = 'X'
            state['moves'] = []
            return {'success': True, 'message': f'Draw! Last piece placed by @{player}'}

        state['turn'] = 'O' if current_symbol == 'X' else 'X'
        return {
            'success': True,
            'message': f'{self.symbols[current_symbol]} placed at {position.upper()} by @{player}. Next: {self.symbols[state["turn"]]}'
        }

    def check_winner(self, board):
        for i in range(self.size):
            if board[i][0] and board[i][0] == board[i][1] == board[i][2]:
                return board[i][0]
            if board[0][i] and board[0][i] == board[1][i] == board[2][i]:
                return board[0][i]
        if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
            return board[0][0]
        if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
            return board[0][2]
        return None

    def is_full(self, board):
        return all(cell is not None for row in board for cell in row)

    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        board = state['board'] if state.get('board') else self.create_board()
        is_active = state.get('board') is not None

        if is_active:
            md = f"\n**Turn:** {self.symbols[state['turn']]}\n\n"
        else:
            md = "\n"

        md += "|   | **A** | **B** | **C** |   |\n"
        md += "|---|:-----:|:-----:|:-----:|:-:|\n"

        for i in range(self.size):
            md += f"| **{i+1}** | "
            for j in range(self.size):
                cell = board[i][j]
                position = f"{chr(65+j)}{i+1}"

                if cell is None:
                    title = f"Tic-Tac-Toe:+Put+{position}"
                    body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
                    link = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={body}"
                    md += f"[{self.symbols[None]}]({link})"
                elif cell == 'X':
                    md += f"<img src=\"{self.img_x}\" width=40px>"
                else:
                    md += f"<img src=\"{self.img_o}\" width=40px>"
                md += " | "
            md += f"**{i+1}** |\n"

        md += "|   | **A** | **B** | **C** |   |\n"

        if not is_active:
            md += "\nClick any square to start!\n"
        else:
            empty = []
            for i in range(self.size):
                for j in range(self.size):
                    if board[i][j] is None:
                        pos = f"{chr(65+j)}{i+1}"
                        title = f"Tic-Tac-Toe:+Put+{pos}"
                        body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
                        link = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={body}"
                        empty.append(f"[{pos}]({link})")
            md += "\n" + " · ".join(empty) + "\n"

            if state.get('moves'):
                md += "\n<details>\n  <summary>Last placements</summary>\n\n"
                md += "| Position | Player |\n| :------: | :----- |\n"
                for m in state['moves'][-5:]:
                    md += f"| `{m['position']}` ({self.symbols[m['symbol']]}) | [@{m['player']}](https://github.com/{m['player']}) |\n"
                md += "\n</details>\n"

        return md
