# README Games

## Tic-Tac-Toe

<!-- TICTACTOE_START -->
*No active game.* [**Start Game →**](https://github.com/tdnb2b2/readme-games/issues/1/comments/new?body=start%20ttt)
<!-- TICTACTOE_END -->

---

## Reversi / Othello

<!-- REVERSI_START -->
*No active game.* [**Start Game →**](https://github.com/tdnb2b2/readme-games/issues/2/comments/new?body=start%20reversi)
<!-- REVERSI_END -->

---

## Number Guessing (1-100)

<!-- GUESS_START -->
*No active game.* [**Start Game →**](https://github.com/tdnb2b2/readme-games/issues/3/comments/new?body=start%20guess)
<!-- GUESS_END -->

---

## Top 10 Players

<!-- LEADERBOARD_START -->
*まだプレイヤーがいません。最初のプレイヤーになろう！*
<!-- LEADERBOARD_END -->

<details>
  <summary>All Participants</summary>

<!-- PARTICIPANTS_START -->
*まだ参加者がいません。最初の参加者になろう！*
<!-- PARTICIPANTS_END -->

</details>

---

<details>
  <summary>How it works</summary>

### Game System

1. **Click a square** on the game board
2. **GitHub Actions** processes your move automatically
3. **README updates** instantly with new game state
4. **You're added** to leaderboard & participants
5. **Invited as collaborator** (read-only, appears in your profile)

### Technical Stack

- **Trigger**: Issue comments
- **Engine**: Python + PyGithub
- **Storage**: Single JSON file
- **Response**: 10-15 seconds
- **Mobile**: Works in GitHub app

### Commands

| Game | Start | Move Format |
|------|-------|-------------|
| Tic-Tac-Toe | `start ttt` | `A1`, `B2`, `C3` |
| Reversi | `start reversi` | `D3`, `E6`, `F5` |
| Number Guess | `start guess` | `50`, `75`, `42` |

</details>

---

Inspired by [@marcizhu](https://github.com/marcizhu/marcizhu)
