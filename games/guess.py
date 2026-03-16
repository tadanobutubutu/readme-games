import re
import json
import random

class NumberGuess:
    def __init__(self):
        self.min_num = 1
        self.max_num = 100

    def _hint(self, guess, target):
        diff = abs(guess - target)
        direction = 'higher' if guess < target else 'lower'

        if diff == 0:
            return None  # handled as correct
        elif diff <= 2:
            if direction == 'higher':
                return ("🔥 On fire! Just a tiny bit higher!", 'fire')
            else:
                return ("🔥 On fire! Just a tiny bit lower!", 'fire')
        elif diff <= 5:
            if direction == 'higher':
                return ("♨️ So close! A little higher.", 'hot')
            else:
                return ("♨️ So close! A little lower.", 'hot')
        elif diff <= 15:
            if direction == 'higher':
                return ("🌡️ Getting warm — go higher.", 'warm')
            else:
                return ("🌡️ Getting warm — go lower.", 'warm')
        elif diff <= 30:
            if direction == 'higher':
                return ("🌤️ Lukewarm. Higher.", 'lukewarm')
            else:
                return ("🌤️ Lukewarm. Lower.", 'lukewarm')
        else:
            if direction == 'higher':
                return ("🧊 Ice cold. Way higher.", 'cold')
            else:
                return ("🧊 Ice cold. Way lower.", 'cold')

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
            msg = f'🎉 Correct! @{player} guessed **{state["number"]}** in {n_attempts} attempt(s)!'
            state['number'] = None
            return {'success': True, 'message': msg}

        hint_text, hint_level = self._hint(value, state['number'])
        msg = f'{hint_text} (attempt #{n_attempts} by @{player} — guessed {value})'
        return {'success': True, 'message': msg}

    def _hint_label(self, guess, target):
        """For render table: returns short label"""
        if target is None:
            return '?'
        diff = abs(guess - target)
        direction = '↑' if guess < target else '↓'
        if diff <= 2:
            return f'🔥 On fire! {direction}'
        elif diff <= 5:
            return f'♨️ So close! {direction}'
        elif diff <= 15:
            return f'🌡️ Warm {direction}'
        elif diff <= 30:
            return f'🌤️ Lukewarm {direction}'
        else:
            return f'🧊 Ice cold {direction}'

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
                    hint = self._hint_label(a['guess'], state.get('number'))
                    md += f'| {i} | **{a["guess"]}** | [@{a["player"]}](https://github.com/{a["player"]}) | {hint} |\n'
                md += '\n</details>\n'

        return md
