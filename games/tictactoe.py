import re

class TicTacToe:
    EMPTY = 'EMPTY'
    X = 'X'
    O = 'O'

    IMG_X = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/274c.svg'
    IMG_O = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/2b55.svg'
    SYM = {X: '❌', O: '⭕', EMPTY: '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'}

    # Parse board state from README hidden comment
    # State format stored as hidden comment inside TICTACTOE markers:
    # <!-- STATE:{"board":[[...]]},{"turn":"X"} -->
    def parse_state(self, section):
        m = re.search(r'<!-- TTT_STATE:(.*?) -->', section)
        if m:
            import json
            return json.loads(m.group(1))
        return {'board': self._empty_board(), 'turn': self.X, 'log': []}

    def _empty_board(self):
        return [[self.EMPTY]*3 for _ in range(3)]

    def place(self, state, position, player):
        board = state['board']
        turn = state['turn']

        col = ord(position[0].upper()) - ord('A')
        row = int(position[1]) - 1

        if not (0 <= row <= 2 and 0 <= col <= 2):
            return {'success': False, 'message': f'❌ Invalid position {position}. Use A1-C3.'}

        if board[row][col] != self.EMPTY:
            return {'success': False, 'message': f'❌ Square {position} is already occupied!'}

        board[row][col] = turn
        log = state.get('log', [])
        log.append({'player': player, 'pos': position.upper(), 'sym': turn})
        state['log'] = log[-10:]  # keep last 10

        winner = self._check_winner(board)
        if winner:
            state['board'] = self._empty_board()
            state['turn'] = self.X
            state['log'] = []
            return {'success': True, 'game_over': True,
                    'message': f'{self.SYM[winner]} wins! Game over. Placed by @{player}'}

        if all(board[r][c] != self.EMPTY for r in range(3) for c in range(3)):
            state['board'] = self._empty_board()
            state['turn'] = self.X
            state['log'] = []
            return {'success': True, 'game_over': True,
                    'message': f'Draw! Last piece placed by @{player}'}

        state['turn'] = self.O if turn == self.X else self.X
        return {'success': True, 'game_over': False,
                'message': f'{self.SYM[turn]} placed at {position.upper()} by @{player}. Next: {self.SYM[state["turn"]]}'}

    def _check_winner(self, board):
        for i in range(3):
            if board[i][0] != self.EMPTY and board[i][0] == board[i][1] == board[i][2]:
                return board[i][0]
            if board[0][i] != self.EMPTY and board[0][i] == board[1][i] == board[2][i]:
                return board[0][i]
        if board[0][0] != self.EMPTY and board[0][0] == board[1][1] == board[2][2]:
            return board[0][0]
        if board[0][2] != self.EMPTY and board[0][2] == board[1][1] == board[2][0]:
            return board[0][2]
        return None

    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        import json
        board = state['board']
        turn = state['turn']

        # Check if any piece is on the board
        has_pieces = any(board[r][c] != self.EMPTY for r in range(3) for c in range(3))

        md = ''
        if has_pieces:
            md += f'**Turn:** {self.SYM[turn]}\n\n'

        # Embed state as hidden comment (single source of truth)
        md += f'<!-- TTT_STATE:{json.dumps(state, separators=(",",":"))} -->\n\n'

        md += '|   | **A** | **B** | **C** |   |\n'
        md += '|---|:-----:|:-----:|:-----:|:-:|\n'
        for r in range(3):
            md += f'| **{r+1}** | '
            for c in range(3):
                cell = board[r][c]
                pos = f'{chr(65+c)}{r+1}'
                if cell == self.EMPTY:
                    url = f'https://github.com/{owner}/{repo}/issues/new?title=Tic-Tac-Toe:+Put+{pos}&body=Just+click+Submit+new+issue'
                    md += f'[{self.SYM[self.EMPTY]}]({url})'
                elif cell == self.X:
                    md += f'<img src="{self.IMG_X}" width=40px>'
                else:
                    md += f'<img src="{self.IMG_O}" width=40px>'
                md += ' | '
            md += f'**{r+1}** |\n'
        md += '|   | **A** | **B** | **C** |   |\n'

        if not has_pieces:
            md += '\nClick any square to start!\n'
        else:
            empty_links = []
            for r in range(3):
                for c in range(3):
                    if board[r][c] == self.EMPTY:
                        pos = f'{chr(65+c)}{r+1}'
                        url = f'https://github.com/{owner}/{repo}/issues/new?title=Tic-Tac-Toe:+Put+{pos}&body=Just+click+Submit+new+issue'
                        empty_links.append(f'[{pos}]({url})')
            md += '\n' + ' · '.join(empty_links) + '\n'

            log = state.get('log', [])
            if log:
                md += '\n<details>\n  <summary>Last placements</summary>\n\n'
                md += '| Position | Player |\n| :------: | :----- |\n'
                for entry in log[-5:]:
                    md += f'| `{entry["pos"]}` ({self.SYM[entry["sym"]]}) | [@{entry["player"]}](https://github.com/{entry["player"]}) |\n'
                md += '\n</details>\n'

        return md
