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

    def _load_stats(self):
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                data = json.load(f)
            # migrate: ensure 'games' key exists
            if 'games' not in data:
                data['games'] = {'tictactoe': 0, 'reversi': 0, 'guess': 0}
            return data
        return {
            'players': {},
            'participants': [],
            'games': {'tictactoe': 0, 'reversi': 0, 'guess': 0}
        }

    def _save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def _record(self, game_key):
        key_map = {'ttt': 'tictactoe', 'rev': 'reversi', 'guess': 'guess'}
        game_type = key_map.get(game_key, game_key)

        # per-player stats
        p = self.stats['players']
        if self.actor not in p:
            p[self.actor] = {'total': 0, 'tictactoe': 0, 'reversi': 0, 'guess': 0}
        p[self.actor]['total'] += 1
        if game_type in p[self.actor]:
            p[self.actor][game_type] += 1
        if self.actor not in self.stats['participants']:
            self.stats['participants'].append(self.actor)

        # per-game stats
        g = self.stats['games']
        if game_type not in g:
            g[game_type] = 0
        g[game_type] += 1

    def parse(self):
        t = self.issue_title

        if self.actor == self.admin_user:
            if re.search(r'reset.*(ox|tictactoe|tic)', t, re.I):
                return 'ttt_reset', None
            if re.search(r'reset.*(reversi|othello)', t, re.I):
                return 'rev_reset', None
            if re.search(r'reset.*(guess)', t, re.I):
                return 'guess_reset', None

        m = re.match(r'Tic-Tac-Toe:\s*Put\s+([A-Ca-c][1-3])\s*$', t)
        if m: return 'ttt', m.group(1).upper()

        m = re.match(r'Reversi:\s*Put\s+([A-Ha-h][1-8])\s*$', t)
        if m: return 'rev', m.group(1).upper()

        m = re.match(r'Number\s+Guess:\s*(\d+)\s*$', t, re.I)
        if m: return 'guess', int(m.group(1))

        if re.match(r'Number\s+Guess:\s*Start', t, re.I):
            return 'guess', 'start'

        return None, None

    def _get_readme(self):
        obj = self.repo.get_contents('README.md')
        return obj, obj.decoded_content.decode('utf-8')

    def _section(self, content, name):
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
            f'Update game by @{self.actor}',
            content,
            readme_obj.sha,
            branch='main'
        )

    def _render_leaderboard(self):
        top = sorted(
            self.stats['players'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:10]
        if not top:
            return '*No players yet. Be the first!*'
        md = '| Rank | Player | Total | Tic-Tac-Toe | Reversi | Number Guess |\n'
        md += '|:----:|--------|:-----:|:-----------:|:-------:|:------------:|\n'
        for i, (player, s) in enumerate(top, 1):
            rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
            md += f'| {rank} | [@{player}](https://github.com/{player}) | {s["total"]} | {s["tictactoe"]} | {s["reversi"]} | {s["guess"]} |\n'
        return md

    def _render_game_stats(self):
        g = self.stats.get('games', {})
        ttt_total = g.get('tictactoe', 0)
        rev_total = g.get('reversi', 0)
        guess_total = g.get('guess', 0)
        grand_total = ttt_total + rev_total + guess_total

        games = [
            ('Tic-Tac-Toe', ttt_total),
            ('Reversi / Othello', rev_total),
            ('Number Guessing', guess_total),
        ]
        games_sorted = sorted(games, key=lambda x: x[1], reverse=True)

        md = f'**Total moves played: {grand_total}**\n\n'
        md += '| Rank | Game | Moves Played |\n'
        md += '|:----:|------|:------------:|\n'
        for i, (name, count) in enumerate(games_sorted, 1):
            rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
            bar_len = int((count / max(grand_total, 1)) * 20)
            bar = '|' * bar_len + '.' * (20 - bar_len)
            md += f'| {rank} | {name} | {count} `{bar}` |\n'
        return md

    def _render_participants(self):
        if not self.stats['participants']:
            return '*No participants yet.*'
        total = len(self.stats['participants'])
        md = f'**Total participants: {total}**\n\n'
        for p in self.stats['participants']:
            n = self.stats['players'].get(p, {}).get('total', 0)
            md += f'[![@{p}](https://img.shields.io/badge/@{p}-{n}_moves-blue)](https://github.com/{p}) '
        return md

    def run(self):
        action, value = self.parse()

        if action is None:
            self.issue.create_comment(
                f'Unknown command: `{self.issue_title}`\n\n'
                'Expected formats:\n'
                '- `Tic-Tac-Toe: Put A1` (A1-C3)\n'
                '- `Reversi: Put D4` (A1-H8)\n'
                '- `Number Guess: 50` (1-100)\n'
                '- `Number Guess: Start New Game`'
            )
            self.issue.edit(state='closed')
            return

        readme_obj, content = self._get_readme()
        result = None

        if action == 'ttt_reset':
            state = {'board': self.ttt._empty_board(), 'turn': self.ttt.X, 'log': []}
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Tic-Tac-Toe reset by @{self.actor}')
            self.issue.edit(state='closed')
            return

        if action == 'rev_reset':
            state = {'board': self.rev._empty_board(), 'turn': self.rev.BLACK, 'log': []}
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Reversi reset by @{self.actor}')
            self.issue.edit(state='closed')
            return

        if action == 'guess_reset':
            state = {'number': None, 'attempts': [], 'solved': False}
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Number Guess reset by @{self.actor}')
            self.issue.edit(state='closed')
            return

        if action == 'ttt':
            section = self._section(content, 'TICTACTOE')
            state = self.ttt.parse_state(section)
            result = self.ttt.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                return
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))

        elif action == 'rev':
            section = self._section(content, 'REVERSI')
            state = self.rev.parse_state(section)
            result = self.rev.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                return
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))

        elif action == 'guess':
            section = self._section(content, 'GUESS')
            state = self.guess.parse_state(section)
            result = self.guess.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                return
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))

        self._record(action)
        self._save_stats()

        content = self._replace_section(content, 'LEADERBOARD', self._render_leaderboard())
        content = self._replace_section(content, 'GAME_STATS', self._render_game_stats())
        content = self._replace_section(content, 'PARTICIPANTS', self._render_participants())

        self._update_readme(content, readme_obj)
        self.issue.create_comment(result['message'])
        self.issue.edit(state='closed')

if __name__ == '__main__':
    GameManager().run()
