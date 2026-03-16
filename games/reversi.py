import re

class Reversi:
    EMPTY = None
    BLACK = 'black'
    WHITE = 'white'

    IMG_BLACK = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26ab.svg'
    IMG_WHITE = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26aa.svg'
    SYM = {BLACK: '⚫', WHITE: '⚪', None: '&nbsp;&nbsp;&nbsp;'}
    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def _empty_board(self):
        board = [[None]*8 for _ in range(8)]
        board[3][3] = board[4][4] = self.WHITE
        board[3][4] = board[4][3] = self.BLACK
        return board

    def parse_state(self, section):
        m = re.search(r'<!-- REV_STATE:(.*?) -->', section)
        if m:
            import json
            return json.loads(m.group(1))
        return {'board': self._empty_board(), 'turn': self.BLACK, 'log': []}

    def place(self, state, position, player):
        board = state['board']
        turn = state['turn']

        col = ord(position[0].upper()) - ord('A')
        row = int(position[1]) - 1

        if not (0 <= row <= 7 and 0 <= col <= 7):
            return {'success': False, 'message': f'❌ Invalid position {position}. Use A1-H8.'}

        flips = self._get_flips(board, row, col, turn)
        if not flips:
            return {'success': False, 'message': f'❌ Invalid placement at {position}. No pieces to flip.'}

        board[row][col] = turn
        for fr, fc in flips:
            board[fr][fc] = turn

        log = state.get('log', [])
        log.append({'player': player, 'pos': position.upper(), 'color': turn})
        state['log'] = log[-10:]

        next_turn = self.WHITE if turn == self.BLACK else self.BLACK
        if not self._has_valid(board, next_turn):
            if not self._has_valid(board, turn):
                winner = self._get_winner(board)
                state['board'] = self._empty_board()
                state['turn'] = self.BLACK
                state['log'] = []
                return {'success': True, 'game_over': True,
                        'message': f'Game over! {winner} wins. Last piece placed by @{player}'}
            next_turn = turn  # skip

        state['turn'] = next_turn
        return {'success': True, 'game_over': False,
                'message': f'{self.SYM[turn]} placed at {position.upper()} by @{player}. Flipped {len(flips)}. Next: {self.SYM[next_turn]}'}

    def _get_flips(self, board, row, col, color):
        if board[row][col] is not None:
            return []
        opp = self.WHITE if color == self.BLACK else self.BLACK
        flips = []
        for dr, dc in self.DIRS:
            tmp = []
            r, c = row+dr, col+dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == opp:
                    tmp.append((r, c))
                elif board[r][c] == color:
                    flips.extend(tmp)
                    break
                else:
                    break
                r, c = r+dr, c+dc
        return flips

    def _has_valid(self, board, color):
        return any(self._get_flips(board, r, c, color)
                   for r in range(8) for c in range(8))

    def _get_winner(self, board):
        b = sum(row.count(self.BLACK) for row in board)
        w = sum(row.count(self.WHITE) for row in board)
        if b > w: return '⚫ Black'
        if w > b: return '⚪ White'
        return 'Draw'

    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        import json
        board = state['board']
        turn = state['turn']

        valid = set()
        for r in range(8):
            for c in range(8):
                if self._get_flips(board, r, c, turn):
                    valid.add(f'{chr(65+c)}{r+1}')

        b_count = sum(row.count(self.BLACK) for row in board)
        w_count = sum(row.count(self.WHITE) for row in board)

        md = f'**Turn:** {self.SYM[turn]} | ⚫ {b_count} – ⚪ {w_count}\n\n'
        md += f'<!-- REV_STATE:{json.dumps(state, separators=(",",":"))} -->\n\n'

        md += '|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n'
        md += '|---|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-:|\n'
        for r in range(8):
            md += f'| **{r+1}** | '
            for c in range(8):
                cell = board[r][c]
                pos = f'{chr(65+c)}{r+1}'
                if cell == self.BLACK:
                    md += f'<img src="{self.IMG_BLACK}" width=36px>'
                elif cell == self.WHITE:
                    md += f'<img src="{self.IMG_WHITE}" width=36px>'
                elif pos in valid:
                    url = f'https://github.com/{owner}/{repo}/issues/new?title=Reversi:+Put+{pos}&body=Just+click+Submit+new+issue'
                    md += f'[{self.SYM[None]}]({url})'
                else:
                    md += self.SYM[None]
                md += ' | '
            md += f'**{r+1}** |\n'
        md += '|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n'

        if valid:
            links = []
            for p in sorted(valid):
                url = f'https://github.com/{owner}/{repo}/issues/new?title=Reversi:+Put+{p}&body=Just+click+Submit+new+issue'
                links.append(f'[{p}]({url})')
            md += '\n' + ' · '.join(links) + '\n'
        else:
            md += '\nNo valid moves!\n'

        log = state.get('log', [])
        if log:
            md += '\n<details>\n  <summary>Last placements</summary>\n\n'
            md += '| Position | Player |\n| :------: | :----- |\n'
            for entry in log[-5:]:
                md += f'| `{entry["pos"]}` ({self.SYM[entry["color"]]}) | [@{entry["player"]}](https://github.com/{entry["player"]}) |\n'
            md += '\n</details>\n'

        return md
