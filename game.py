#!/usr/bin/env python3
import os
import re
import sys
from github import Github
from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.guess import NumberGuess

TTT_PAT   = re.compile(r'^Tic-Tac-Toe:\s*(?:Put|Move)\s+[A-Ca-c][1-3]\s*$')
REV_PAT   = re.compile(r'^Reversi:\s*Put\s+[A-Ha-h][1-8]\s*$')
GUESS_PAT = re.compile(r'^Number\s+Guess:\s*\d+\s*$', re.I)


class GameManager:
    def __init__(self):
        self.g         = Github(os.environ['GITHUB_TOKEN'])
        self.repo      = self.g.get_repo(os.environ['REPO'])
        self.issue_num = int(os.environ['ISSUE_NUMBER'])
        self.issue     = self.repo.get_issue(self.issue_num)
        self.actor     = os.environ['ACTOR']
        self.issue_title = os.environ.get('ISSUE_TITLE', '').strip()
        self.admin_user  = 'tadanobutubutu'
        self.owner, self.repo_name = os.environ['REPO'].split('/')

        self.ttt   = TicTacToe()
        self.rev   = Reversi()
        self.guess = NumberGuess()

    # ------------------------------------------------------------------ #
    #  issues から統計をリアルタイム集計                                    #
    # ------------------------------------------------------------------ #
    def _compute_stats(self):
        """閉じた全 issues のタイトルをパースして統計を返す。"""
        players = {}   # {login: {total, tictactoe, reversi, guess}}
        games   = {'tictactoe': 0, 'reversi': 0, 'guess': 0}

        # 現在処理中の issue（まだ closed になっていない）を先行カウント
        current_type = self._title_to_type(self.issue_title)
        if current_type:
            self._add_count(players, games, self.actor, current_type)

        # 閉じた全 issues を走査
        for issue in self.repo.get_issues(state='closed'):
            if issue.number == self.issue_num:
                continue          # 現 issue は上で処理済み
            t = issue.title.strip()
            gtype = self._title_to_type(t)
            if gtype is None:
                continue
            login = issue.user.login
            self._add_count(players, games, login, gtype)

        participants = sorted(players.keys(),
                              key=lambda p: players[p]['total'], reverse=True)
        return {'players': players, 'participants': participants, 'games': games}

    @staticmethod
    def _title_to_type(title):
        if TTT_PAT.match(title):   return 'tictactoe'
        if REV_PAT.match(title):   return 'reversi'
        if GUESS_PAT.match(title): return 'guess'
        return None

    @staticmethod
    def _add_count(players, games, login, gtype):
        if login not in players:
            players[login] = {'total': 0, 'tictactoe': 0, 'reversi': 0, 'guess': 0}
        players[login]['total']  += 1
        players[login][gtype]    += 1
        games[gtype]             += 1

    # ------------------------------------------------------------------ #
    #  レンダリング                                                         #
    # ------------------------------------------------------------------ #
    def _render_leaderboard(self, stats):
        top = sorted(stats['players'].items(),
                     key=lambda x: x[1]['total'], reverse=True)[:10]
        if not top:
            return '*No players yet. Be the first!*'
        md  = '| Rank | Player | Total | Tic-Tac-Toe | Reversi | Number Guess |\n'
        md += '|:----:|--------|:-----:|:-----------:|:-------:|:------------:|\n'
        for i, (player, s) in enumerate(top, 1):
            rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
            md += (f'| {rank} | [@{player}](https://github.com/{player}) '
                   f'| {s["total"]} | {s["tictactoe"]} | {s["reversi"]} | {s["guess"]} |\n')
        return md

    def _render_game_stats(self, stats):
        g = stats['games']
        ttt_total   = g.get('tictactoe', 0)
        rev_total   = g.get('reversi', 0)
        guess_total = g.get('guess', 0)
        grand_total = ttt_total + rev_total + guess_total
        if grand_total == 0:
            return '*No moves played yet.*'
        games_sorted = sorted([
            ('Tic-Tac-Toe',        ttt_total),
            ('Reversi / Othello',  rev_total),
            ('Number Guessing',    guess_total),
        ], key=lambda x: x[1], reverse=True)
        md  = f'**Total moves played: {grand_total}**\n\n'
        md += '| Rank | Game | Moves |\n'
        md += '|:----:|------|:-----:|\n'
        for i, (name, count) in enumerate(games_sorted, 1):
            rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
            bar_len = int(count / grand_total * 20)
            bar = '#' * bar_len + '-' * (20 - bar_len)
            pct = round(count / grand_total * 100)
            md += f'| {rank} | {name} | {count} ({pct}%) `{bar}` |\n'
        return md

    def _render_participants(self, stats):
        if not stats['participants']:
            return '*No participants yet.*'
        total = len(stats['participants'])
        md = f'**Total participants: {total}**\n\n'
        for p in stats['participants']:
            n = stats['players'][p]['total']
            md += f'[![@{p}](https://img.shields.io/badge/@{p}-{n}_moves-blue)](https://github.com/{p}) '
        return md

    # ------------------------------------------------------------------ #
    #  ユーティリティ                                                       #
    # ------------------------------------------------------------------ #
    def parse(self):
        t = self.issue_title
        if self.actor == self.admin_user:
            if re.search(r'reset.*(ox|tictactoe|tic)', t, re.I):   return 'ttt_reset',   None
            if re.search(r'reset.*(reversi|othello)',  t, re.I):   return 'rev_reset',   None
            if re.search(r'reset.*(guess)',            t, re.I):   return 'guess_reset', None
        m = re.match(r'Tic-Tac-Toe:\s*Put\s+([A-Ca-c][1-3])\s*$', t)
        if m: return 'ttt', m.group(1).upper()
        m = re.match(r'Reversi:\s*Put\s+([A-Ha-h][1-8])\s*$', t)
        if m: return 'rev', m.group(1).upper()
        m = re.match(r'Number\s+Guess:\s*(\d+)\s*$', t, re.I)
        if m: return 'guess', int(m.group(1))
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
            content, readme_obj.sha, branch='main'
        )

    # ------------------------------------------------------------------ #
    #  メイン処理                                                           #
    # ------------------------------------------------------------------ #
    def run(self):
        action, value = self.parse()

        if action is None:
            self.issue.create_comment(
                f'Unknown command: `{self.issue_title}`\n\n'
                'Expected formats:\n'
                '- `Tic-Tac-Toe: Put A1` (A1-C3)\n'
                '- `Reversi: Put D4` (A1-H8)\n'
                '- `Number Guess: 50` (1-100)'
            )
            self.issue.edit(state='closed')
            sys.exit(0)

        readme_obj, content = self._get_readme()
        result = None

        # --- リセット系（ランキング更新あり）---
        if action == 'ttt_reset':
            state = {'board': self.ttt._empty_board(), 'turn': self.ttt.X, 'log': []}
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))
            stats   = self._compute_stats()
            content = self._replace_section(content, 'LEADERBOARD',  self._render_leaderboard(stats))
            content = self._replace_section(content, 'GAME_STATS',   self._render_game_stats(stats))
            content = self._replace_section(content, 'PARTICIPANTS', self._render_participants(stats))
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Tic-Tac-Toe reset by @{self.actor}')
            self.issue.edit(state='closed')
            sys.exit(0)

        if action == 'rev_reset':
            state = {'board': self.rev._empty_board(), 'turn': self.rev.BLACK, 'log': []}
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))
            stats   = self._compute_stats()
            content = self._replace_section(content, 'LEADERBOARD',  self._render_leaderboard(stats))
            content = self._replace_section(content, 'GAME_STATS',   self._render_game_stats(stats))
            content = self._replace_section(content, 'PARTICIPANTS', self._render_participants(stats))
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Reversi reset by @{self.actor}')
            self.issue.edit(state='closed')
            sys.exit(0)

        if action == 'guess_reset':
            state = {'number': None, 'attempts': [], 'solved': False}
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))
            stats   = self._compute_stats()
            content = self._replace_section(content, 'LEADERBOARD',  self._render_leaderboard(stats))
            content = self._replace_section(content, 'GAME_STATS',   self._render_game_stats(stats))
            content = self._replace_section(content, 'PARTICIPANTS', self._render_participants(stats))
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Number Guess reset by @{self.actor}')
            self.issue.edit(state='closed')
            sys.exit(0)

        # --- ゲーム手 ---
        if action == 'ttt':
            section = self._section(content, 'TICTACTOE')
            state   = self.ttt.parse_state(section)
            result  = self.ttt.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))

        elif action == 'rev':
            section = self._section(content, 'REVERSI')
            state   = self.rev.parse_state(section)
            result  = self.rev.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))

        elif action == 'guess':
            section = self._section(content, 'GUESS')
            state   = self.guess.parse_state(section)
            result  = self.guess.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))

        # issues から統計を集計してランキング更新
        stats   = self._compute_stats()
        content = self._replace_section(content, 'LEADERBOARD',  self._render_leaderboard(stats))
        content = self._replace_section(content, 'GAME_STATS',   self._render_game_stats(stats))
        content = self._replace_section(content, 'PARTICIPANTS', self._render_participants(stats))

        self._update_readme(content, readme_obj)
        self.issue.create_comment(result['message'])
        self.issue.edit(state='closed')
        sys.exit(0)


if __name__ == '__main__':
    GameManager().run()
