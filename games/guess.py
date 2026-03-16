import re
import json
import random

class NumberGuess:
    def __init__(self):
        self.min_num = 1
        self.max_num = 100

    def _hint(self, guess, target):
        diff = abs(guess - target)
        arrow = '🔺' if guess < target else '🔻'

        if diff <= 2:
            return f'Extremely close {arrow}'
        elif diff <= 5:
            return f'Very close {arrow}'
        elif diff <= 15:
            return f'Close {arrow}'
        elif diff <= 30:
            return f'Higher {arrow}' if guess < target else f'Lower {arrow}'
        else:
            return f'Way higher {arrow}' if guess < target else f'Way lower {arrow}'

    def parse_state(self, section):
        m = re.search(r'<!-- GUESS_STATE:(.*?) -->', section)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        return {'number': None, 'attempts': [], 'solved': False}

    def place(self, state, value, player):
        if value == 'start':
            state['number'] = random.randint(self.min_num, self.max_num)
            state['attempts'] = []
            state['solved'] = False
            return {'success': True, 'message': f'New round started by @{player}! Guess a number between {self.min_num} and {self.max_num}.'}

        if state.get('number') is None:
            state['number'] = random.randint(self.min_num, self.max_num)
            state['attempts'] = []
            state['solved'] = False

        if state.get('solved'):
            return {'success': False, 'message': 'Already solved! Start a new round.'}

        if not isinstance(value, int) or value < self.min_num or value > self.max_num:
            return {'success': False, 'message': f'Enter a number between {self.min_num} and {self.max_num}'}

        state['attempts'].append({'player': player, 'guess': value})
        n_attempts = len(state['attempts'])

        if value == state['number']:
            state['solved'] = True
            msg = f'Correct! @{player} guessed {state["number"]} in {n_attempts} attempt(s).'
            state['number'] = None
            return {'success': True, 'message': msg}

        hint = self._hint(value, state['number'])
        msg = f'{value} — {hint} (attempt #{n_attempts} by @{player})'
        return {'success': True, 'message': msg}

    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        is_active = state.get('number') is not None and not state.get('solved', False)
        attempts = state.get('attempts', [])

        lo, hi = self.min_num, self.max_num
        if is_active and attempts:
            for a in attempts:
                g = a['guess']
                if g < state['number']:
                    lo = max(lo, g + 1)
                else:
                    hi = min(hi, g - 1)

        md = ''
        if is_active:
            md += f'**Guess the secret number** | Range: **{lo} – {hi}** | Attempts: {len(attempts)}\n\n'
        else:
            md += '**Guess the secret number between 1 and 100.**\n\n'

        md += f'<!-- GUESS_STATE:{json.dumps(state, separators=(",",":"))} -->\n\n'

        if is_active:
            mid = (lo + hi) // 2
            q1 = (lo + mid) // 2
            q3 = (mid + hi) // 2
            suggestions = sorted(set([q1, mid, q3]))
        else:
            suggestions = [25, 50, 75]

        links = []
        for n in suggestions:
            url = f'https://github.com/{owner}/{repo}/issues/new?title=Number+Guess:+{n}&body=Just+click+Submit+new+issue'
            links.append(f'[{n}]({url})')
        md += 'Click to guess: ' + ' · '.join(links) + '\n\n'

        if not is_active:
            start_url = f'https://github.com/{owner}/{repo}/issues/new?title=Number+Guess:+Start+New+Game&body=Just+click+Submit+new+issue'
            md += f'[Start a new round →]({start_url})\n'
        else:
            if attempts:
                md += '<details>\n  <summary>Last 5 attempts</summary>\n\n'
                md += '| # | Guess | Player | Hint |\n| :-: | :---: | :----- | :--- |\n'
                for i, a in enumerate(attempts[-5:], max(1, len(attempts) - 4)):
                    hint = self._hint(a['guess'], state.get('number'))
                    md += f'| {i} | **{a["guess"]}** | [@{a["player"]}](https://github.com/{a["player"]}) | {hint} |\n'
                md += '\n</details>\n'

        return md
