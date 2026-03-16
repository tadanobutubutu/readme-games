#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from github import Github, GithubException
from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.guess import NumberGuess

class GameManager:
    def __init__(self):
        self.g = Github(os.environ['GITHUB_TOKEN'])
        self.repo = self.g.get_repo(os.environ['REPO'])
        self.issue_num = int(os.environ['ISSUE_NUMBER'])
        self.issue = self.repo.get_issue(self.issue_num)
        self.actor = os.environ['ACTOR']
        self.issue_title = os.environ.get('ISSUE_TITLE', '').strip()
        self.admin_user = 'tadanobutubutu'
        self.owner, self.repo_name = os.environ['REPO'].split('/')

        self.stats_file = Path('game_stats.json')
        self.stats = self._load_stats()

        self.ttt = TicTacToe()
        self.rev = Reversi()
        self.guess = NumberGuess()

    # ------------------------------------------------------------------ stats
    def _load_stats(self):
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                return json.load(f)
        return {'players': {}, 'participants': []}

    def _save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def _record(self, game_type):
        p = self.stats['players']
        if self.actor not in p:
            p[self.actor] = {'total': 0, 'tictactoe': 0, 'reversi': 0, 'guess': 0}
        p[self.actor]['total'] += 1
        p[self.actor][game_type] += 1
        if self.actor not in self.stats['participants']:
            self.stats['participants'].append(self.actor)

    # ------------------------------------------------------------------ parse
    def parse(self):
        t = self.issue_title

        # Admin reset
        if self.actor == self.admin_user:
            if re.search(r'リセット\s*(ox|oxゲーム|まるばつ|tictactoe|tic)', t, re.I):
                return 'ttt_reset', None
            if re.search(r'リセット\s*(オセロ|オセロゲーム|reversi|リバーシ)', t, re.I):
                return 'rev_reset', None
            if re.search(r'リセット\s*(数当て?|guess|ゲス)', t, re.I):
                return 'guess_reset', None

        m = re.match(r'Tic-Tac-Toe:\s*Put\s+([A-Ca-c][1-3])', t)
        if m: return 'ttt', m.group(1).upper()

        m = re.match(r'Reversi:\s*Put\s+([A-Ha-h][1-8])', t)
        if m: return 'rev', m.group(1).upper()

        m = re.match(r'Number\s+Guess:\s*(\d+)', t, re.I)
        if m: return 'guess', int(m.group(1))

        if re.match(r'Number\s+Guess:\s*Start', t, re.I):
            return 'guess', 'start'

        return None, None

    # ------------------------------------------------------------------ readme
    def _get_readme(self):
        obj = self.repo.get_contents('README.md')
        return obj, obj.decoded_content.decode('utf-8')

    def _section(self, content, name):
        """Extract content between <!-- NAME_START --> and <!-- NAME_END -->"""
        m = re.search(rf'<!-- {name}_START -->(.*?)<!-- {name}_END -->', content, re.DOTALL)
        return m.group(1) if m else ''

    def _replace_section(self, content, name, new_body):
        return re.sub(
            rf'<!-- {name}_START -->.*?<!-- {name}_END -->',
            f'<!-- {name}_START -->\n{new_body}\n<!-- {name}_END -->',
            content, flags=re.DOTALL
        )

    def _update_readme(self, content, readme_obj):
        self.repo.update_file(
            'README.md',
            f'🎮 Update game state by @{self.actor}',
            content,
            readme_obj.sha,
            branch='main'
        )

    def _render_leaderboard(self):
        top = sorted(self.stats['players'].items(), key=lambda x: x[1]['total'], reverse=True)[:10]
        if not top:
            return '*No players yet. Be the first!*'
        md = '| Rank | Player | Total | TTT | Reversi | Guess |\n'
        md += '|------|--------|-------|-----|---------|-------|\n'
        for i, (p, s) in enumerate(top, 1):
            rank = ['1st','2nd','3rd'][i-1] if i <= 3 else f'{i}th'
            md += f'| {rank} | @{p} | {s["total"]} | {s["tictactoe"]} | {s["reversi"]} | {s["guess"]} |\n'
        return md

    def _render_participants(self):
        if not self.stats['participants']:
            return '*No participants yet.*'
        total = len(self.stats['participants'])
        md = f'**Total participants: {total}**\n\n'
        for p in self.stats['participants']:
            n = self.stats['players'].get(p, {}).get('total', 0)
            md += f'[![@{p}](https://img.shields.io/badge/@{p}-{n}_plays-blue)](https://github.com/{p}) '
        return md

    # ------------------------------------------------------------------ reset
    def _reset_ttt(self, readme_obj, content):
        state = {'board': self.ttt._empty_board(), 'turn': self.ttt.X, 'log': []}
        new_section = self.ttt.render(state, self.owner, self.repo_name)
        content = self._replace_section(content, 'TICTACTOE', new_section)
        self._update_readme(content, readme_obj)
        return '♻️ Tic-Tac-Toe reset by @' + self.actor

    def _reset_rev(self, readme_obj, content):
        state = {'board': self.rev._empty_board(), 'turn': self.rev.BLACK, 'log': []}
        new_section = self.rev.render(state, self.owner, self.repo_name)
        content = self._replace_section(content, 'REVERSI', new_section)
        self._update_readme(content, readme_obj)
        return '♻️ Reversi reset by @' + self.actor

    def _reset_guess(self, readme_obj, content):
        # load guess state and reset
        guess_section = self._section(content, 'GUESS')
        state = self.guess.parse_state(guess_section)
        state['number'] = None
        state['attempts'] = []
        state['solved'] = False
        new_section = self.guess.render(state)
        content = self._replace_section(content, 'GUESS', new_section)
        self._update_readme(content, readme_obj)
        return '♻️ Number Guess reset by @' + self.actor

    # ------------------------------------------------------------------ run
    def run(self):
        action, value = self.parse()

        if action is None:
            self.issue.create_comment(
                f'⚠️ Unknown command: `{self.issue_title}`\n\n'
                'Expected:\n'
                '- `Tic-Tac-Toe: Put A1` (A1–C3)\n'
                '- `Reversi: Put D4` (A1–H8)\n'
                '- `Number Guess: 50` (1–100)\n'
                '- `Number Guess: Start New Game`'
            )
            self.issue.edit(state='closed')
            return

        readme_obj, content = self._get_readme()

        # --- resets ---
        if action == 'ttt_reset':
            msg = self._reset_ttt(readme_obj, content)
            self.issue.create_comment(msg)
            self.issue.edit(state='closed')
            return
        if action == 'rev_reset':
            msg = self._reset_rev(readme_obj, content)
            self.issue.create_comment(msg)
            self.issue.edit(state='closed')
            return
        if action == 'guess_reset':
            msg = self._reset_guess(readme_obj, content)
            self.issue.create_comment(msg)
            self.issue.edit(state='closed')
            return

        # --- tictactoe ---
        if action == 'ttt':
            section = self._section(content, 'TICTACTOE')
            state = self.ttt.parse_state(section)
            result = self.ttt.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                return
            new_section = self.ttt.render(state, self.owner, self.repo_name)
            content = self._replace_section(content, 'TICTACTOE', new_section)

        # --- reversi ---
        elif action == 'rev':
            section = self._section(content, 'REVERSI')
            state = self.rev.parse_state(section)
            result = self.rev.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                return
            new_section = self.rev.render(state, self.owner, self.repo_name)
            content = self._replace_section(content, 'REVERSI', new_section)

        # --- number guess ---
        elif action == 'guess':
            section = self._section(content, 'GUESS')
            state = self.guess.parse_state(section)
            result = self.guess.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                return
            new_section = self.guess.render(state)
            content = self._replace_section(content, 'GUESS', new_section)

        # update leaderboard & participants
        self._record(action if action in ('tictactoe','reversi','guess') else
                     ('tictactoe' if action=='ttt' else 'reversi' if action=='rev' else 'guess'))
        self._save_stats()

        lb = self._render_leaderboard()
        content = self._replace_section(content, 'LEADERBOARD', lb)
        pa = self._render_participants()
        content = self._replace_section(content, 'PARTICIPANTS', pa)

        self._update_readme(content, readme_obj)
        self.issue.create_comment(result['message'])
        self.issue.edit(state='closed')

if __name__ == '__main__':
    GameManager().run()
