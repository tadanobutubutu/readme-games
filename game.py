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
        self.comment_body = os.environ.get('COMMENT_BODY', '')
        
        self.data_file = Path('game_data.json')
        self.load_data()
        
        self.games = {
            'tictactoe': TicTacToe(),
            'reversi': Reversi(),
            'guess': NumberGuess()
        }
    
    def load_data(self):
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'players': {},
                'tictactoe': {'board': None, 'turn': 'X', 'moves': []},
                'reversi': {'board': None, 'turn': 'black', 'moves': []},
                'guess': {'number': None, 'attempts': [], 'solved': False}
            }
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def update_player_stats(self, game_type):
        if self.actor not in self.data['players']:
            self.data['players'][self.actor] = {'total': 0, 'tictactoe': 0, 'reversi': 0, 'guess': 0}
        self.data['players'][self.actor]['total'] += 1
        self.data['players'][self.actor][game_type] += 1
    
    def get_top_players(self, limit=10):
        return sorted(self.data['players'].items(), key=lambda x: x[1]['total'], reverse=True)[:limit]
    
    def invite_collaborator(self):
        try:
            # Check if user is already a collaborator
            collabs = [c.login for c in self.repo.get_collaborators()]
            if self.actor not in collabs and self.actor != self.repo.owner.login:
                self.repo.add_to_collaborators(self.actor, permission='push')
                self.issue.create_comment(f"🎉 @{self.actor} has been invited as a collaborator! Check your email for the invitation.")
        except GithubException as e:
            # User might not have public email or invitation already sent
            pass
    
    def parse_move(self):
        body = self.comment_body.lower().strip()
        
        # Tic-Tac-Toe: "ttt A1" or just "A1" if in tictactoe issue
        ttt_match = re.search(r'(?:ttt\s+)?([a-c][1-3])', body)
        if ttt_match:
            return 'tictactoe', ttt_match.group(1).upper()
        
        # Reversi: "reversi D3" or just "D3" if in reversi issue
        rev_match = re.search(r'(?:reversi\s+)?([a-h][1-8])', body)
        if rev_match:
            return 'reversi', rev_match.group(1).upper()
        
        # Number Guess: "guess 50" or just number
        guess_match = re.search(r'(?:guess\s+)?(\d+)', body)
        if guess_match:
            return 'guess', int(guess_match.group(1))
        
        # Game start commands
        if 'start' in body:
            if 'ttt' in body or 'tictactoe' in body or 'tic' in body:
                return 'tictactoe', 'start'
            elif 'reversi' in body or 'othello' in body:
                return 'reversi', 'start'
            elif 'guess' in body or 'number' in body:
                return 'guess', 'start'
        
        return None, None
    
    def update_readme(self):
        readme = self.repo.get_contents('README.md')
        content = readme.decoded_content.decode('utf-8')
        
        # Update game sections
        for game_name, game in self.games.items():
            marker_start = f"<!-- {game_name.upper()}_START -->"
            marker_end = f"<!-- {game_name.upper()}_END -->"
            
            if marker_start in content and marker_end in content:
                game_section = game.render(self.data[game_name])
                pattern = f"{re.escape(marker_start)}.*?{re.escape(marker_end)}"
                replacement = f"{marker_start}\n{game_section}\n{marker_end}"
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Update leaderboard
        leaderboard = self.render_leaderboard()
        lb_start = "<!-- LEADERBOARD_START -->"
        lb_end = "<!-- LEADERBOARD_END -->"
        if lb_start in content and lb_end in content:
            pattern = f"{re.escape(lb_start)}.*?{re.escape(lb_end)}"
            replacement = f"{lb_start}\n{leaderboard}\n{lb_end}"
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        self.repo.update_file('README.md', f'Update README after move by @{self.actor}', content, readme.sha, branch='main')
    
    def render_leaderboard(self):
        top = self.get_top_players()
        if not top:
            return "*No players yet. Be the first!*"
        
        md = "| Rank | Player | Total Moves | TTT | Reversi | Guess |\n"
        md += "|------|--------|-------------|-----|---------|-------|\n"
        for i, (player, stats) in enumerate(top, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            md += f"| {medal} | @{player} | {stats['total']} | {stats['tictactoe']} | {stats['reversi']} | {stats['guess']} |\n"
        return md
    
    def run(self):
        game_type, move = self.parse_move()
        
        if not game_type:
            return
        
        game = self.games[game_type]
        result = game.make_move(self.data[game_type], move, self.actor)
        
        if result['success']:
            self.update_player_stats(game_type)
            self.invite_collaborator()
            self.save_data()
            self.update_readme()
            
            if result.get('message'):
                self.issue.create_comment(result['message'])
        else:
            self.issue.create_comment(f"❌ {result.get('message', 'Invalid move')}")

if __name__ == '__main__':
    manager = GameManager()
    manager.run()
