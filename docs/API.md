# 📚 Game API Reference

## Overview

This document describes the internal API for creating new games in the README Games system.

## Game Class Interface

### Required Methods

Every game class must implement these two methods:

#### 1. `make_move(state, move, player)`

Process a player's move and update the game state.

**Parameters:**
- `state` (dict): Current game state. Structure defined by each game.
- `move` (str | int | any): Parsed move from user comment. Type depends on game.
- `player` (str): GitHub username of the player making the move.

**Returns:**
```python
{
    'success': bool,      # True if move was valid and executed
    'message': str        # Human-readable result message
}
```

**Special Cases:**
- `move == 'start'`: Initialize a new game
- `state` is empty/None: No active game

**Example Implementation:**
```python
def make_move(self, state, move, player):
    # Handle game start
    if move == 'start':
        state['board'] = self.create_board()
        state['turn'] = 'X'
        return {
            'success': True,
            'message': f'🎮 New game started by @{player}!'
        }
    
    # Validate game exists
    if not state.get('board'):
        return {
            'success': False,
            'message': 'No active game. Start with "start game"'
        }
    
    # Validate move format
    if not self.is_valid_format(move):
        return {
            'success': False,
            'message': 'Invalid move format'
        }
    
    # Execute move
    if self.execute(state, move):
        # Check win/lose/draw
        result = self.check_game_over(state)
        
        if result:
            return {
                'success': True,
                'message': f'🎉 {result}!'
            }
        
        return {
            'success': True,
            'message': f'✅ Move executed by @{player}'
        }
    else:
        return {
            'success': False,
            'message': 'Invalid move'
        }
```

#### 2. `render(state)`

Render the current game state as Markdown for display in README.

**Parameters:**
- `state` (dict): Current game state

**Returns:**
- `str`: Markdown-formatted string

**Example Implementation:**
```python
def render(self, state):
    if not state.get('board'):
        return "*No active game. Start with: `start game`*"
    
    md = "\n**Current Turn:** " + state['turn'] + "\n\n"
    
    # Render board
    md += self.render_board(state['board'])
    
    # Add instructions
    md += "\n**How to play:** Comment with your move\n"
    
    # Recent moves
    if state.get('moves'):
        md += "\n**Last 3 moves:**\n\n"
        for m in state['moves'][-3:]:
            md += f"- {m['move']} by @{m['player']}\n"
    
    return md
```

## State Structure

### Game Manager State

The global state file `game_data.json` has this structure:

```python
{
    "players": {
        "username": {
            "total": int,          # Total moves across all games
            "tictactoe": int,      # Moves in Tic-Tac-Toe
            "reversi": int,        # Moves in Reversi
            "guess": int,          # Moves in Number Guess
            "yourgame": int        # Your game moves
        }
    },
    "tictactoe": {              # Game-specific state
        # Your game defines this structure
    },
    "reversi": {...},
    "guess": {...},
    "yourgame": {...}
}
```

### Game-Specific State

Each game defines its own state structure. Examples:

**Tic-Tac-Toe:**
```python
{
    "board": [
        ["X", None, "O"],
        [None, "X", None],
        ["O", None, None]
    ],
    "turn": "X",                # Current player
    "moves": [                  # Move history
        {
            "player": "user1",
            "move": "A1",
            "symbol": "X"
        }
    ]
}
```

**Number Guess:**
```python
{
    "number": 42,               # Secret number
    "attempts": [               # Guess history
        {"player": "user1", "guess": 50}
    ],
    "solved": False            # Game status
}
```

## Move Parsing

### Adding Your Game to Parser

In `game.py`, update the `parse_move()` method:

```python
def parse_move(self):
    body = self.comment_body.lower().strip()
    
    # Your game pattern
    your_match = re.search(r'(?:yourgame\s+)?([a-z0-9]+)', body)
    if your_match:
        return 'yourgame', your_match.group(1).upper()
    
    # Handle start command
    if 'start' in body:
        if 'yourgame' in body:
            return 'yourgame', 'start'
    
    # ... other games ...
    
    return None, None
```

### Regex Patterns

**Examples:**

| Game | Pattern | Matches |
|------|---------|----------|
| Tic-Tac-Toe | `r'([a-c][1-3])'` | A1, B2, C3 |
| Reversi | `r'([a-h][1-8])'` | D3, E6, F5 |
| Number Guess | `r'(\d+)'` | 42, 99, 1 |
| Chess | `r'([a-h][1-8][a-h][1-8])'` | e2e4, g1f3 |

**Tips:**
- Use `(?:prefix\s+)?` for optional game name prefix
- Capture group `()` for the actual move
- Use case-insensitive matching

## Registering Your Game

### Step 1: Import

```python
# In game.py
from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.guess import NumberGuess
from games.yourgame import YourGame  # Add this
```

### Step 2: Initialize

```python
class GameManager:
    def __init__(self):
        # ...
        self.games = {
            'tictactoe': TicTacToe(),
            'reversi': Reversi(),
            'guess': NumberGuess(),
            'yourgame': YourGame()  # Add this
        }
```

### Step 3: Add State Template

```python
def load_data(self):
    if self.data_file.exists():
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)
    else:
        self.data = {
            'players': {},
            'tictactoe': {...},
            'reversi': {...},
            'guess': {...},
            'yourgame': {           # Add this
                'your_field': 'initial_value'
            }
        }
```

### Step 4: Update README Template

```markdown
### 🎲 Your Game

<!-- YOURGAME_START -->
*No active game. Start with: `start yourgame`*
<!-- YOURGAME_END -->

**Start new game:** [Click here](https://github.com/tadanobutubutu/readme-games/issues/new?title=Your%20Game&body=start%20yourgame)
```

## Best Practices

### 1. State Validation

Always check state validity:

```python
def make_move(self, state, move, player):
    # Check if game initialized
    if 'board' not in state or state['board'] is None:
        return {'success': False, 'message': 'No active game'}
    
    # Check if game already over
    if state.get('winner'):
        return {'success': False, 'message': 'Game already finished'}
```

### 2. Clear Error Messages

```python
# Bad
return {'success': False, 'message': 'Error'}

# Good
return {
    'success': False,
    'message': 'Position A5 is out of bounds. Valid: A1-C3'
}
```

### 3. Emoji for Visual Feedback

```python
# Success
'✅ Move executed'
'🎉 You won!'
'✅ Game started'

# Errors
'❌ Invalid move'
'⚠️ Position already taken'

# Info
'🎮 Game in progress'
'📈 Too low'
'📉 Too high'
```

### 4. Efficient Win Checking

```python
# Bad: O(n^3) - check all positions
for state in all_possible_states:
    if is_winning(state):
        return True

# Good: O(n) - check only affected positions
def check_winner(board, last_move_row, last_move_col):
    # Only check row, column, and diagonals containing last move
    pass
```

### 5. Move History

```python
def make_move(self, state, move, player):
    # Record every move
    if 'moves' not in state:
        state['moves'] = []
    
    state['moves'].append({
        'player': player,
        'move': move,
        'timestamp': time.time(),
        'additional': 'context'
    })
```

## Testing Your Game

### Unit Tests

```python
import pytest
from games.yourgame import YourGame

def test_game_start():
    game = YourGame()
    state = {}
    result = game.make_move(state, 'start', 'testuser')
    
    assert result['success'] == True
    assert state['board'] is not None

def test_valid_move():
    game = YourGame()
    state = {'board': game.create_board(), 'turn': 'X'}
    result = game.make_move(state, 'A1', 'testuser')
    
    assert result['success'] == True
    assert state['board'][0][0] == 'X'

def test_invalid_move():
    game = YourGame()
    state = {'board': None}
    result = game.make_move(state, 'A1', 'testuser')
    
    assert result['success'] == False
```

### Local Testing

```bash
# Set environment variables
export GITHUB_TOKEN="ghp_your_token"
export ISSUE_NUMBER="1"
export COMMENT_BODY="A1"
export ACTOR="testuser"
export REPO="owner/repo"

# Run game manager
python game.py

# Check output
cat game_data.json
cat README.md
```

## Common Patterns

### Turn-Based Games

```python
def make_move(self, state, move, player):
    # Alternate turns
    state['turn'] = 'O' if state['turn'] == 'X' else 'X'
```

### Score Tracking

```python
def render(self, state):
    score = self.calculate_score(state)
    return f"**Score:** Player 1: {score[0]} - Player 2: {score[1]}"
```

### Multi-Round Games

```python
{
    "rounds": [
        {"winner": "user1", "moves": [...]},
        {"winner": "user2", "moves": [...]}
    ],
    "current_round": 2
}
```

### Undo/Redo

```python
def make_move(self, state, move, player):
    if move == 'undo':
        if len(state['moves']) > 0:
            state['moves'].pop()
            self.rebuild_board(state)
            return {'success': True, 'message': 'Move undone'}
```

## Performance Tips

### 1. Lazy Rendering

```python
# Don't render if state hasn't changed
if state.get('render_cache_valid'):
    return state['render_cache']

rendered = self._render_slow(state)
state['render_cache'] = rendered
state['render_cache_valid'] = True
return rendered
```

### 2. Efficient Data Structures

```python
# Bad: List of lists (slow lookup)
board = [[None] * 8 for _ in range(8)]
if board[row][col] == 'X':  # O(1) but verbose

# Good: Dictionary (fast, sparse)
board = {}  # {(row, col): 'X'}
if board.get((row, col)) == 'X':  # O(1) and clean
```

### 3. Minimal State

```python
# Bad: Store redundant data
state = {
    'board': [...],
    'num_x': 5,      # Redundant
    'num_o': 4,      # Redundant
    'empty': 0       # Redundant
}

# Good: Compute on demand
state = {'board': [...]}

def count_pieces(board):
    return board.count('X'), board.count('O')
```

---

**Happy coding! Create amazing games!** 🎮🚀
