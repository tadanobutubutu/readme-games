#!/usr/bin/env python3
"""
One-time migration script.
Scans ALL closed issues, checks bot comment for success,
and rebuilds game_stats.json from scratch.

Success patterns per game:
  Reversi / Tic-Tac-Toe : 'placed at'
  Number Guess (any)    : proximity hints | correct | new round
"""
import os
import re
import json
from pathlib import Path
from github import Github

TTT_RE   = re.compile(r'^Tic-Tac-Toe:\s*Put\s+[A-Ca-c][1-3]\s*$')
REV_RE   = re.compile(r'^Reversi:\s*Put\s+[A-Ha-h][1-8]\s*$')
GUESS_RE = re.compile(r'^Number\s+Guess:\s*\d+\s*$', re.I)

# Proximity-based hints + legacy 'too high/low' + correct
GUESS_SUCCESS_RE = re.compile(
    r'on fire|so close|getting warm|lukewarm|ice cold|too high|too low|correct|guessed',
    re.I
)

SUCCESS = {
    'tictactoe': re.compile(r'placed at', re.I),
    'reversi':   re.compile(r'placed at', re.I),
    'guess':     GUESS_SUCCESS_RE,
}

def main():
    token = os.environ['GITHUB_TOKEN']
    repo_name = os.environ['REPO']

    g = Github(token)
    repo = g.get_repo(repo_name)

    stats = {
        'players': {},
        'participants': [],
        'games': {'tictactoe': 0, 'reversi': 0, 'guess': 0}
    }

    print('Fetching all closed issues...')
    issues = repo.get_issues(state='closed')
    total = 0
    valid = 0

    for issue in issues:
        title = issue.title.strip()
        actor = issue.user.login

        if TTT_RE.match(title):
            game_type = 'tictactoe'
        elif REV_RE.match(title):
            game_type = 'reversi'
        elif GUESS_RE.match(title):
            game_type = 'guess'
        else:
            continue

        total += 1
        success_pat = SUCCESS[game_type]

        is_valid = False
        for comment in issue.get_comments():
            if comment.user.login == 'github-actions[bot]' and success_pat.search(comment.body):
                is_valid = True
                break

        if not is_valid:
            print(f'  SKIP #{issue.number} [{game_type}]: {title}')
            continue

        valid += 1
        print(f'  OK   #{issue.number} [{game_type}] @{actor}: {title}')

        stats['games'][game_type] += 1

        p = stats['players']
        if actor not in p:
            p[actor] = {'total': 0, 'tictactoe': 0, 'reversi': 0, 'guess': 0}
        p[actor]['total'] += 1
        p[actor][game_type] += 1

        if actor not in stats['participants']:
            stats['participants'].append(actor)

    print(f'\nDone. Scanned {total} game issues, {valid} valid moves.')
    print(f'Game totals : {stats["games"]}')
    print(f'Players     : {list(stats["players"].keys())}')

    out = Path('game_stats.json')
    with open(out, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f'Written to {out}')

if __name__ == '__main__':
    main()
