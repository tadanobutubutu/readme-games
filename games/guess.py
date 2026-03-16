import random

class NumberGuess:
    def __init__(self):
        self.min_num = 1
        self.max_num = 100
        self.issue_number = 3

    def set_issue_number(self, num):
        self.issue_number = num

    def make_move(self, state, move, player):
        if move == 'start':
            state['number'] = random.randint(self.min_num, self.max_num)
            state['attempts'] = []
            state['solved'] = False
            return {'success': True, 'message': f'New round started by @{player}. Guess a number between {self.min_num} and {self.max_num}.'}

        if state['number'] is None:
            state['number'] = random.randint(self.min_num, self.max_num)
            state['attempts'] = []
            state['solved'] = False

        if state['solved']:
            return {'success': False, 'message': 'Already solved. Start a new round with "start guess"'}

        guess = move
        if not isinstance(guess, int) or guess < self.min_num or guess > self.max_num:
            return {'success': False, 'message': f'Enter a number between {self.min_num} and {self.max_num}'}

        state['attempts'].append({'player': player, 'guess': guess})

        if guess == state['number']:
            state['solved'] = True
            n = len(state['attempts'])
            msg = f'Correct! @{player} guessed {state["number"]} in {n} attempt(s).'
            state['number'] = None
            return {'success': True, 'message': msg}
        elif guess < state['number']:
            return {'success': True, 'message': f'{guess} is too low (attempt #{len(state["attempts"])} by @{player})'}
        else:
            return {'success': True, 'message': f'{guess} is too high (attempt #{len(state["attempts"])} by @{player})'}

    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        is_active = state['number'] is not None and not state.get('solved', False)
        attempts = state.get('attempts', [])

        lo, hi = self.min_num, self.max_num
        if is_active and attempts:
            for a in attempts:
                g = a['guess']
                if g < state['number']:
                    lo = max(lo, g + 1)
                else:
                    hi = min(hi, g - 1)

        if is_active:
            md = f"\n**Guess the secret number** | Range: **{lo} – {hi}** | Attempts: {len(attempts)}\n\n"
        else:
            md = "\n**Guess the secret number between 1 and 100.**\n\n"

        if is_active:
            mid = (lo + hi) // 2
            q1 = (lo + mid) // 2
            q3 = (mid + hi) // 2
            suggestions = sorted(set([q1, mid, q3]))
        else:
            suggestions = [25, 50, 75]

        links = []
        for n in suggestions:
            # New issue format with title and body pre-filled
            title = f"Number+Guess:+{n}"
            body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
            url = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={body}"
            links.append(f"[{n}]({url})")

        md += "Click to guess: " + " · ".join(links) + "\n\n"

        if not is_active:
            # Start new game link
            title = "Number+Guess:+Start+New+Game"
            body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
            start_url = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={body}"
            md += f"[Start a new round \u2192]({start_url})\n"
        else:
            if attempts:
                md += "<details>\n  <summary>Last 5 attempts</summary>\n\n"
                md += "| # | Guess | Player | Hint |\n| :-: | :---: | :----- | :--- |\n"
                for i, a in enumerate(attempts[-5:], len(attempts) - min(5, len(attempts)) + 1):
                    hint = 'too low' if a['guess'] < state['number'] else 'too high'
                    md += f"| {i} | **{a['guess']}** | [@{a['player']}](https://github.com/{a['player']}) | {hint} |\n"
                md += "\n</details>\n"

        return md
