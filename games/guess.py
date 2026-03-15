import random

class NumberGuess:
    def __init__(self):
        self.min_num = 1
        self.max_num = 100
    
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
            state['number'] = None  # Reset
            return {'success': True, 'message': msg}
        elif guess < state['number']:
            msg = f"📈 {guess} is too low! Try again. (Attempt #{len(state['attempts'])} by @{player})"
        else:
            msg = f"📉 {guess} is too high! Try again. (Attempt #{len(state['attempts'])} by @{player})"
        
        return {'success': True, 'message': msg}
    
    def render(self, state):
        if state['number'] is None:
            return "*No active game. Start with: `start guess` or `start number`*"
        
        if state['solved']:
            return "*Game solved! Start a new game.*"
        
        md = f"\n**Guess a number between {self.min_num} and {self.max_num}**\n\n"
        md += f"**Attempts so far:** {len(state['attempts'])}\n\n"
        
        if state['attempts']:
            md += "**Recent attempts:**\n\n"
            for att in state['attempts'][-5:]:
                if att['guess'] < state['number']:
                    hint = "📈 Too low"
                else:
                    hint = "📉 Too high"
                md += f"- {att['guess']} by @{att['player']} - {hint}\n"
        
        md += "\n**How to play:** Comment a number (e.g., `50`, `guess 75`)\n"
        
        return md
