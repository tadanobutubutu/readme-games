# 🏛️ Architecture Overview

## System Design

### High-Level Flow

```
User comments on issue
        ↓
GitHub Actions triggered
        ↓
Workflow starts (Ubuntu latest)
        ↓
Checkout code + Install Python 3.11
        ↓
Install dependencies (cached)
        ↓
Execute game.py
        ↓
Parse move & validate
        ↓
Update game state
        ↓
Update README.md
        ↓
Commit & push changes
        ↓
Invite player as collaborator
        ↓
Post comment with result
```

## Components

### 1. GitHub Actions Workflow (`.github/workflows/game-action.yml`)

**Triggers:**
- `issues.opened` - When new issue is created
- `issue_comment.created` - When comment is posted

**Permissions:**
- `issues: write` - Post comments
- `contents: write` - Update README and commit
- `pull-requests: write` - Invite collaborators

**Steps:**
1. Checkout repository (main branch)
2. Setup Python 3.11 with pip cache
3. Install dependencies from requirements.txt
4. Execute game.py with environment variables
5. Commit and push if changes detected

### 2. Game Manager (`game.py`)

**Responsibilities:**
- Parse issue comments for game commands
- Load and save game state (JSON)
- Delegate moves to game classes
- Update README with new state
- Manage player statistics
- Invite players as collaborators

**Key Methods:**
- `parse_move()` - Extract game type and move from comment
- `update_player_stats()` - Track player move counts
- `invite_collaborator()` - Add player to repository
- `update_readme()` - Replace game sections in README
- `render_leaderboard()` - Generate top 10 players table

### 3. Game Classes (`games/*.py`)

Each game implements two key methods:

#### `make_move(state, move, player)`

**Input:**
- `state`: Dictionary containing current game state
- `move`: Parsed move (string or int)
- `player`: GitHub username

**Output:**
```python
{
    'success': True/False,
    'message': 'Human-readable result'
}
```

**Logic:**
1. Check if game needs to start
2. Validate move format and bounds
3. Execute move and update state
4. Check win/lose/draw conditions
5. Return result

#### `render(state)`

**Input:**
- `state`: Current game state

**Output:**
- Markdown string for README section

**Content:**
- Current board/state visualization
- Move instructions
- Recent moves history
- Score/status information

## Data Flow

### State Management

**File:** `game_data.json`

**Structure:**
```json
{
  "players": {
    "username": {
      "total": 42,
      "tictactoe": 15,
      "reversi": 20,
      "guess": 7
    }
  },
  "tictactoe": {
    "board": [["X", null, "O"], ...],
    "turn": "X",
    "moves": [{"player": "...", "move": "A1", "symbol": "X"}]
  },
  "reversi": {...},
  "guess": {...}
}
```

**Read/Write:**
- Loaded at start of workflow
- Modified by game logic
- Saved before README update
- Committed to repository

### README Update

**Markers:**
```markdown
<!-- TICTACTOE_START -->
... game content ...
<!-- TICTACTOE_END -->
```

**Process:**
1. Read current README.md from repository
2. For each game, call `render(state)`
3. Replace content between markers using regex
4. Update leaderboard section similarly
5. Commit updated README with API

## Performance Optimizations

### 1. Minimal Dependencies

**Only PyGithub** for GitHub API interaction
- No heavy frameworks (Django, Flask)
- No database (PostgreSQL, MongoDB)
- No caching layer (Redis)
- Pure Python standard library

### 2. Pip Caching

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'  # Cache dependencies
```

First run: ~30s
Cached runs: ~5s

### 3. Single JSON File

**Why not database?**
- JSON read/write: <1ms
- PostgreSQL connection: 50-100ms
- File size: <10KB for 1000+ moves
- No network latency
- No connection pooling needed

### 4. Efficient Parsing

**Regex patterns:**
```python
# Compiled patterns are cached by Python
ttt_match = re.search(r'(?:ttt\s+)?([a-c][1-3])', body)
```

**Time complexity:**
- O(n) where n = comment length (usually <100 chars)
- Instant for typical inputs

### 5. Direct API Updates

**No intermediate services:**
- GitHub Actions → Python → GitHub API
- No webhooks to external servers
- No queue processing
- No background jobs

## Security

### 1. Permissions

**Workflow uses `GITHUB_TOKEN`:**
- Scoped to repository only
- Temporary credentials
- Automatically rotated
- No personal access tokens

### 2. Input Validation

**All moves validated:**
- Format checking (regex)
- Bounds checking
- Type checking
- State verification

**No code execution:**
- Comments are never `eval()`'d
- No dynamic imports
- No shell commands from user input

### 3. Collaborator Invitations

**Safe invitation logic:**
```python
try:
    # Only invite if not already collaborator
    if actor not in existing_collaborators:
        repo.add_to_collaborators(actor, permission='push')
except GithubException:
    pass  # Fail silently if invitation fails
```

## Scalability

### Current Limits

- **GitHub Actions:** 2000 minutes/month (free tier)
- **Workflow duration:** ~10-15 seconds per move
- **Theoretical max moves:** ~8000/month
- **Practical limit:** ~1000-2000 moves/month

### If Scaling Needed

1. **Batch updates** - Process multiple moves together
2. **Webhook server** - External service for faster response
3. **Database** - PostgreSQL for larger state
4. **Caching** - Redis for frequently accessed data
5. **CDN** - Cache static README renders

### Current Design Choice

**Optimized for:**
- ✅ Simplicity
- ✅ Reliability
- ✅ Zero cost
- ✅ Easy to fork
- ✅ No maintenance

**Not optimized for:**
- ❌ Thousands of concurrent users
- ❌ Sub-second response times
- ❌ Real-time multiplayer

## Error Handling

### Graceful Failures

```python
try:
    # Invite collaborator
    repo.add_to_collaborators(actor)
except GithubException:
    # Don't fail workflow if invitation fails
    pass
```

### User Feedback

**Invalid moves:**
```python
return {
    'success': False,
    'message': 'Position already taken'
}
```

**Result posted as issue comment:**
- ✅ Success messages
- ❌ Error messages
- 🎉 Game over notifications

## Extensibility

### Adding New Games

1. Create `games/newgame.py`
2. Implement `make_move()` and `render()`
3. Register in `game.py`
4. Add README section
5. Update move parsing

**No workflow changes needed!**

The system automatically:
- Detects new game commands
- Updates appropriate sections
- Tracks statistics

## Monitoring

### GitHub Actions Logs

**View workflow runs:**
https://github.com/tadanobutubutu/readme-games/actions

**Each run shows:**
- Trigger event (issue/comment)
- Execution duration
- Success/failure status
- Full Python logs

### Debugging

**Add debug logging:**
```python
import os
if os.environ.get('DEBUG'):
    print(f"Parsed move: {move}")
    print(f"State before: {state}")
```

**Test locally:**
```bash
export GITHUB_TOKEN="ghp_..."
export ISSUE_NUMBER="1"
export COMMENT_BODY="A1"
export ACTOR="testuser"
export REPO="owner/repo"

python game.py
```

## Future Enhancements

### Potential Features

1. **AI Opponents** - Computer players for single-player
2. **Tournaments** - Bracket-style competitions
3. **Achievements** - Badges for milestones
4. **Replay System** - View game history
5. **Mobile App** - Native game interface
6. **Live Updates** - WebSocket for real-time
7. **Voice Control** - Accessibility feature
8. **Analytics** - Game statistics dashboard

### Technical Improvements

1. **Type hints** - Full type annotations
2. **Unit tests** - Pytest coverage
3. **CI/CD** - Automated testing
4. **Docker** - Containerized execution
5. **Async** - Concurrent API calls
6. **GraphQL** - More efficient API

---

**Architecture designed for simplicity, speed, and fun!** ⚡
