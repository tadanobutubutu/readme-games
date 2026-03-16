# Contributing to README Games

Thank you for your interest in contributing! There are several ways you can help:

## Play the Games!

The easiest way to contribute is to play! When you make a move:

1. Your **name appears in the participants list**
2. Your moves are **recorded in the leaderboard**
3. You help **test the system** and find bugs

**No special permissions needed** - just play and have fun!

## Report Bugs

Found a bug? Please [open an issue](https://github.com/tadanobutubutu/readme-games/issues/new) with:

- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

## Add New Games

Want to add a new game? Here's how:

### 1. Create Your Game Class

Create a new file in `games/yourgame.py`:

```python
class YourGame:
    def __init__(self):
        # Initialize game constants
        pass
    
    def make_move(self, state, move, player):
        """
        Process a move and update state.
        
        Args:
            state: Current game state (dict)
            move: Player's move (str or int)
            player: GitHub username (str)
        
        Returns:
            {'success': bool, 'message': str}
        """
        # Handle 'start' command
        if move == 'start':
            # Initialize game state
            return {'success': True, 'message': 'Game started!'}
        
        # Validate and execute move
        # Update state
        # Return result
        pass
    
    def render(self, state):
        """
        Render game state as Markdown.
        
        Args:
            state: Current game state (dict)
        
        Returns:
            Markdown string for README
        """
        return "*Game state here*"
```

### 2. Register Your Game

In `game.py`, add your game:

```python
from games.yourgame import YourGame

# In GameManager.__init__:
self.games = {
    'tictactoe': TicTacToe(),
    'reversi': Reversi(),
    'guess': NumberGuess(),
    'yourgame': YourGame()  # Add this
}

# In GameManager.load_data:
self.data = {
    'players': {},
    'participants': [],
    'tictactoe': {...},
    'reversi': {...},
    'guess': {...},
    'yourgame': {'your': 'initial_state'}  # Add this
}
```

### 3. Update README.md

Add your game section:

```markdown
### Your Game Name

<!-- YOURGAME_START -->
*No active game. Start with: `start yourgame`*
<!-- YOURGAME_END -->

**Start new game:** [Click here](https://github.com/tadanobutubutu/readme-games/issues/new?title=Your%20Game&body=start%20yourgame)
```

### 4. Add Move Parsing

In `game.py`, update `parse_move()` method:

```python
def parse_move(self):
    body = self.comment_body.lower().strip()
    
    # Your game pattern
    your_match = re.search(r'(?:yourgame\s+)?(your_pattern)', body)
    if your_match:
        return 'yourgame', your_match.group(1)
    
    # ... existing patterns ...
```

### 5. Test Your Game

1. Fork the repository
2. Make your changes
3. Test locally with mock GitHub events
4. Create a pull request

## Code Style

- Use **Python 3.11** features
- Keep functions **short and focused**
- Add **docstrings** to public methods
- Follow **PEP 8** style guide
- Prioritize **performance** and **simplicity**

## Performance Guidelines

- Minimize **external dependencies**
- Use **efficient algorithms** (O(n) or better when possible)
- Avoid **unnecessary file I/O**
- Keep **JSON state compact**
- Use **regex for parsing** (fast)

## Quality Checklist

Before submitting a PR:

- [ ] Game logic is correct and tested
- [ ] Move parsing is robust
- [ ] README section renders properly
- [ ] State persists correctly
- [ ] Error messages are helpful
- [ ] Performance is optimized
- [ ] Code follows style guide

## Submit Your Contribution

1. Fork the repository
2. Create a feature branch: `git checkout -b add-your-game`
3. Commit your changes: `git commit -am 'Add YourGame'`
4. Push to the branch: `git push origin add-your-game`
5. Submit a pull request

## Questions?

Feel free to [open an issue](https://github.com/tadanobutubutu/readme-games/issues/new) or reach out to the maintainers!

---

**Thank you for making README Games better!**
