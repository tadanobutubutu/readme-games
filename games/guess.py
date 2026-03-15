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
            return {'success': True, 'message': f"🎮 New number guessing game started by @{player}! Guess a number between {self.min_num} and {self.max_num}."}
        
        if state['number'] is None:
            return {'success': False, 'message': 'No active game. Start with "start guess"'}
        
        if state['solved']:
            return {'success': False, 'message': 'Game already solved! Start a new game.'}
        
        guess = move
        if not isinstance(guess, int) or guess < self.min_num or guess > self.max_num:
            return {'success': False, 'message': f'Invalid guess. Enter number between {self.min_num} and {self.max_num}'}
        
        state['attempts'].append({'player': player, 'guess': guess})
        
        if guess == state['number']:
            state['solved'] = True
            attempts = len(state['attempts'])
            msg = f"🎉 Correct! @{player} guessed the number {state['number']} in {attempts} attempt(s)!"
            state['number'] = None
            return {'success': True, 'message': msg}
        elif guess < state['number']:
            msg = f"📈 {guess} is too low! Try again. (Attempt #{len(state['attempts'])} by @{player})"
        else:
            msg = f"📉 {guess} is too high! Try again. (Attempt #{len(state['attempts'])} by @{player})"
        
        return {'success': True, 'message': msg}
    
    def get_suggested_numbers(self, state):
        """Get smart number suggestions based on previous attempts"""
        if not state['attempts']:
            return [25, 50, 75]
        
        guesses = [a['guess'] for a in state['attempts']]
        low = max([g for g in guesses if g < state['number']], default=self.min_num)
        high = min([g for g in guesses if g > state['number']], default=self.max_num)
        
        # Binary search suggestions
        mid = (low + high) // 2
        quarter = (low + mid) // 2
        three_quarter = (mid + high) // 2
        
        suggestions = sorted(set([quarter, mid, three_quarter]))
        return suggestions[:3]  # Return top 3
    
    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        if state['number'] is None:
            return "*No active game.* [**Start Game →**](https://github.com/{}/{}/issues/{}/comments/new?body=start%20guess)".format(owner, repo, self.issue_number)
        
        if state['solved']:
            return "*Game solved! Start a new game.*"
        
        md = "\n**🎲 Guess the secret number!**\n\n"
        md += f"**Range:** {self.min_num} - {self.max_num} | **Attempts:** {len(state['attempts'])}\n\n"
        
        # Calculate range based on attempts
        if state['attempts']:
            guesses = [a['guess'] for a in state['attempts']]
            lows = [g for g in guesses if g < state['number']]
            highs = [g for g in guesses if g > state['number']]
            
            current_min = max(lows) + 1 if lows else self.min_num
            current_max = min(highs) - 1 if highs else self.max_num
            
            md += f"🎯 **Current range:** {current_min} - {current_max}\n\n"
        
        # Suggested numbers as clickable buttons
        suggestions = self.get_suggested_numbers(state)
        if suggestions:
            md += "**⚡ Quick guess:** "
            for num in suggestions:
                link = f"https://github.com/{owner}/{repo}/issues/{self.issue_number}/comments/new?body={num}"
                md += f"[`{num}`]({link}) "
            md += "\n\n"
        
        # Recent attempts table
        if state['attempts']:
            md += "<details>\n  <summary>📊 Last 5 attempts</summary>\n\n"
            md += "| # | Guess | Player | Hint |\n"
            md += "| :-: | :---: | :----- | :--- |\n"
            for i, att in enumerate(state['attempts'][-5:], 1):
                if att['guess'] < state['number']:
                    hint = "📈 Too low"
                else:
                    hint = "📉 Too high"
                md += f"| {len(state['attempts'])-5+i} | **{att['guess']}** | [@{att['player']}](https://github.com/{att['player']}) | {hint} |\n"
            md += "\n</details>\n"
        
        md += "\n**✏️ Or comment any number** between {} and {}\n".format(
            max([a['guess'] for a in state['attempts'] if a['guess'] < state['number']], default=self.min_num) + 1 if state['attempts'] else self.min_num,
            min([a['guess'] for a in state['attempts'] if a['guess'] > state['number']], default=self.max_num) - 1 if state['attempts'] else self.max_num
        )
        
        return md
