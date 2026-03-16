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
        self.issue_title = os.environ.get('ISSUE_TITLE', '')
        
        self.data_file = Path('game_data.json')
        self.load_data()
        
        self.games = {
            'tictactoe': TicTacToe(),
            'reversi': Reversi(),
            'guess': NumberGuess()
        }
        
        if 'issue_numbers' in self.data:
            for game_name, game in self.games.items():
                if game_name in self.data['issue_numbers']:
                    if hasattr(game, 'set_issue_number'):
                        game.set_issue_number(self.data['issue_numbers'][game_name])
    
    def load_data(self):
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'players': {},
                'participants': [],
                'issue_numbers': {'tictactoe': 1, 'reversi': 2, 'guess': 3},
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
        
        if self.actor not in self.data['participants']:
            self.data['participants'].append(self.actor)
    
    def invite_as_read_only_collaborator(self):
        try:
            if self.repo.has_in_collaborators(self.actor):
                return
            self.repo.add_to_collaborators(self.actor, permission='pull')
            print(f"Invited @{self.actor} as read-only collaborator")
        except GithubException as e:
            print(f"Could not invite @{self.actor}: {e.data.get('message', str(e))}")
            pass
    
    def get_top_players(self, limit=10):
        return sorted(self.data['players'].items(), key=lambda x: x[1]['total'], reverse=True)[:limit]
    
    def parse_move(self):
        """
        Parse game information from issue title.
        Expected formats:
        - Tic-Tac-Toe: Move A1
        - Reversi: Move D4
        - Number Guess: 50
        - Number Guess: Start New Game
        """
        title = self.issue_title.strip()
        
        # Tic-Tac-Toe: Move A1 to C3
        ttt_match = re.match(r'Tic-Tac-Toe:\s*Move\s+([A-C][1-3])', title, re.IGNORECASE)
        if ttt_match:
            return 'tictactoe', ttt_match.group(1).upper()
        
        # Reversi: Move A1 to H8
        rev_match = re.match(r'Reversi:\s*Move\s+([A-H][1-8])', title, re.IGNORECASE)
        if rev_match:
            return 'reversi', rev_match.group(1).upper()
        
        # Number Guess: 1-100
        guess_match = re.match(r'Number\s+Guess:\s*(\d+)', title, re.IGNORECASE)
        if guess_match:
            return 'guess', int(guess_match.group(1))
        
        # Number Guess: Start New Game
        if re.match(r'Number\s+Guess:\s*Start', title, re.IGNORECASE):
            return 'guess', 'start'
        
        return None, None
    
    def update_readme(self):
        readme = self.repo.get_contents('README.md')
        content = readme.decoded_content.decode('utf-8')
        
        owner, repo_name = self.repo.full_name.split('/')
        
        for game_name, game in self.games.items():
            marker_start = f"<!-- {game_name.upper()}_START -->"
            marker_end = f"<!-- {game_name.upper()}_END -->"
            
            if marker_start in content and marker_end in content:
                if hasattr(game, 'render') and game_name in ['tictactoe', 'reversi']:
                    game_section = game.render(self.data[game_name], owner=owner, repo=repo_name)
                else:
                    game_section = game.render(self.data[game_name])
                
                pattern = f"{re.escape(marker_start)}.*?{re.escape(marker_end)}"
                replacement = f"{marker_start}\n{game_section}\n{marker_end}"
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        leaderboard = self.render_leaderboard()
        lb_start = "<!-- LEADERBOARD_START -->"
        lb_end = "<!-- LEADERBOARD_END -->"
        if lb_start in content and lb_end in content:
            pattern = f"{re.escape(lb_start)}.*?{re.escape(lb_end)}"
            replacement = f"{lb_start}\n{leaderboard}\n{lb_end}"
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        participants_section = self.render_participants()
        p_start = "<!-- PARTICIPANTS_START -->"
        p_end = "<!-- PARTICIPANTS_END -->"
        if p_start in content and p_end in content:
            pattern = f"{re.escape(p_start)}.*?{re.escape(p_end)}"
            replacement = f"{p_start}\n{participants_section}\n{p_end}"
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        self.repo.update_file('README.md', f'Update README after move by @{self.actor}', content, readme.sha, branch='main')
    
    def render_leaderboard(self):
        top = self.get_top_players()
        if not top:
            return "*No players yet. Be the first!*"
        
        md = "| Rank | Player | Total | TTT | Reversi | Guess |\n"
        md += "|------|--------|-------|-----|---------|-------|\n"
        for i, (player, stats) in enumerate(top, 1):
            medal = "1st" if i == 1 else "2nd" if i == 2 else "3rd" if i == 3 else f"{i}th"
            md += f"| {medal} | @{player} | {stats['total']} | {stats['tictactoe']} | {stats['reversi']} | {stats['guess']} |\n"
        return md
    
    def render_participants(self):
        if not self.data['participants']:
            return "*No participants yet.*"
        
        total = len(self.data['participants'])
        md = f"**Total participants: {total}**\n\n"
        
        for participant in self.data['participants']:
            moves = self.data['players'].get(participant, {}).get('total', 0)
            md += f"[![@{participant}](https://img.shields.io/badge/@{participant}-{moves}_moves-blue)]" 
            md += f"(https://github.com/{participant}) "
        
        return md
    
    def run(self):
        game_type, move = self.parse_move()
        
        if not game_type:
            self.issue.create_comment(
                f"\u26a0\ufe0f Invalid game command in title: `{self.issue_title}`\n\n"
                "Expected format:\n"
                "- `Tic-Tac-Toe: Move A1` (A1 to C3)\n"
                "- `Reversi: Move D4` (A1 to H8)\n"
                "- `Number Guess: 50` (1 to 100)\n"
                "- `Number Guess: Start New Game`"
            )
            self.issue.edit(state='closed')
            return
        
        game = self.games[game_type]
        result = game.make_move(self.data[game_type], move, self.actor)
        
        if result['success']:
            self.update_player_stats(game_type)
            
            if self.data['players'][self.actor]['total'] == 1:
                self.invite_as_read_only_collaborator()
            
            self.save_data()
            self.update_readme()
            
            if result.get('message'):
                self.issue.create_comment(result['message'])
            
            self.issue.edit(state='closed')
        else:
            self.issue.create_comment(f"❌ Error: {result.get('message', 'Invalid move')}")
            self.issue.edit(state='closed')

if __name__ == '__main__':
    manager = GameManager()
    manager.run()
