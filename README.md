# README Games

<!--
AI_INSTRUCTIONS:
=== テストプレイのルール ===
1. 必ず get_file_contents で README.md を取得してから手を打つ
2. issue の title はリンクの title 属性そのままをコピーする（改変禁止）
3. issue の body は常に「Just click Submit new issue」固定
4. issue 発行後、get_comments でコメントが返るまでポーリングして結果を確認する
5. 結果確認後、README.md を再取得して盤面・ランキングを検証する
6. 有効手リスト（テキストリンク行）に載っていないマスは絶対に打たない

=== 管理者限定リセットコマンド（issue title に書いてそのまま submit） ===
- Tic-Tac-Toe リセット : reset ox  / reset tictactoe / reset tic
- Reversi リセット     : reset reversi / reset othello
- 数字当てリセット     : reset guess
※ リセットコマンドは tadanobutubutu アカウントのみ有効

=== ランキング更新タイミング ===
- 毎手ごとに自動更新される（手動操作不要）
- 勝利記録は issue コメントの以下パターンから検出：
  TTT: "❌ wins!" / "⭕ wins!"
  Reversi: "Game over! ⚫ Black wins" / "Game over! ⚪ White wins"
-->

## Tic-Tac-Toe

<!-- TICTACTOE_START -->
<!-- TTT_STATE:{"board":[["EMPTY","EMPTY","EMPTY"],["EMPTY","EMPTY","EMPTY"],["EMPTY","EMPTY","EMPTY"]],"turn":"X","log":[]} -->

|   | **A** | **B** | **C** |   |
|---|:-----:|:-----:|:-----:|:-:|
| **1** | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+A1&body=Just+click+Submit+new+issue) | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+B1&body=Just+click+Submit+new+issue) | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+C1&body=Just+click+Submit+new+issue) | **1** |
| **2** | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+A2&body=Just+click+Submit+new+issue) | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+B2&body=Just+click+Submit+new+issue) | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+C2&body=Just+click+Submit+new+issue) | **2** |
| **3** | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+A3&body=Just+click+Submit+new+issue) | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+B3&body=Just+click+Submit+new+issue) | [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Tic-Tac-Toe:+Put+C3&body=Just+click+Submit+new+issue) | **3** |
|   | **A** | **B** | **C** |   |

Click any square to start!

<!-- TICTACTOE_END -->

---

## Reversi / Othello

<!-- REVERSI_START -->
**Turn:** ⚫ | ⚫ 2 – ⚪ 2

<!-- REV_STATE:{"board":[["empty","empty","empty","empty","empty","empty","empty","empty"],["empty","empty","empty","empty","empty","empty","empty","empty"],["empty","empty","empty","empty","empty","empty","empty","empty"],["empty","empty","empty","white","black","empty","empty","empty"],["empty","empty","empty","black","white","empty","empty","empty"],["empty","empty","empty","empty","empty","empty","empty","empty"],["empty","empty","empty","empty","empty","empty","empty","empty"],["empty","empty","empty","empty","empty","empty","empty","empty"]],"turn":"black","log":[]} -->

|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |
|---|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-:|
| **1** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **1** |
| **2** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **2** |
| **3** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | [&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+D3&body=Just+click+Submit+new+issue) | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **3** |
| **4** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | [&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+C4&body=Just+click+Submit+new+issue) | <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26aa.svg" width=36px> | <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26ab.svg" width=36px> | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **4** |
| **5** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26ab.svg" width=36px> | <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/26aa.svg" width=36px> | [&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+F5&body=Just+click+Submit+new+issue) | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **5** |
| **6** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | [&nbsp;&nbsp;&nbsp;](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+E6&body=Just+click+Submit+new+issue) | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **6** |
| **7** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **7** |
| **8** | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; | **8** |
|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |

[C4](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+C4&body=Just+click+Submit+new+issue) · [D3](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+D3&body=Just+click+Submit+new+issue) · [E6](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+E6&body=Just+click+Submit+new+issue) · [F5](https://github.com/tdnb2b2/readme-games/issues/new?title=Reversi:+Put+F5&body=Just+click+Submit+new+issue)

<!-- REVERSI_END -->

---

## Number Guessing (1-100)

<!-- GUESS_START -->
**Guess the secret number between 1 and 100.**

<!-- GUESS_STATE:{"number":null,"attempts":[{"player":"kk5fgxtdxb-debug","guess":50},{"player":"kk5fgxtdxb-debug","guess":63},{"player":"kk5fgxtdxb-debug","guess":73},{"player":"kk5fgxtdxb-debug","guess":87},{"player":"kk5fgxtdxb-debug","guess":83},{"player":"kk5fgxtdxb-debug","guess":78},{"player":"kk5fgxtdxb-debug","guess":80}],"solved":true} -->

Click to guess: [25](https://github.com/tdnb2b2/readme-games/issues/new?title=Number+Guess:+25&body=Just+click+Submit+new+issue) · [50](https://github.com/tdnb2b2/readme-games/issues/new?title=Number+Guess:+50&body=Just+click+Submit+new+issue) · [75](https://github.com/tdnb2b2/readme-games/issues/new?title=Number+Guess:+75&body=Just+click+Submit+new+issue)


<!-- GUESS_END -->

---

## Top 10 Players

<!-- LEADERBOARD_START -->
| Rank | Player | Total | TTT | Reversi | Guess | ❌W | ⭕W | ⚫W | ⚪W |
|:----:|--------|:-----:|:---:|:-------:|:-----:|:---:|:---:|:---:|:---:|
| 1st | [@tadanobutubutu](https://github.com/tadanobutubutu) | 120 | 30 | 71 | 19 | 3 | 1 | 1 | 0 |
| 2nd | [@kk5fgxtdxb-debug](https://github.com/kk5fgxtdxb-debug) | 7 | 0 | 0 | 7 | 0 | 0 | 0 | 0 |

**Game wins — ❌: 3 ⭕: 1 ⚫: 1 ⚪: 0**

<!-- LEADERBOARD_END -->

<details>
  <summary>All Participants</summary>

<!-- PARTICIPANTS_START -->
**Total participants: 2**

[![@tadanobutubutu](https://img.shields.io/badge/@tadanobutubutu-120_moves-blue)](https://github.com/tadanobutubutu) [![@kk5fgxtdxb-debug](https://img.shields.io/badge/@kk5fgxtdxb-debug-7_moves-blue)](https://github.com/kk5fgxtdxb-debug) 
<!-- PARTICIPANTS_END -->

</details>

---

## Most Played Games

<!-- GAME_STATS_START -->
**Total moves played: 127**

| Rank | Game | Moves |
|:----:|------|:-----:|
| 1st | Reversi / Othello | 71 (56%) `###########---------` |
| 2nd | Tic-Tac-Toe | 30 (24%) `####----------------` |
| 3rd | Number Guessing | 26 (20%) `####----------------` |

<!-- GAME_STATS_END -->

---

<details>
  <summary>How it works</summary>

Click a square on the board. This opens a pre-filled issue form. Just click "Submit new issue" and GitHub Actions will process your placement and update this README in ~15 seconds.

**All game information is encoded in the issue title:**
- Tic-Tac-Toe: `Tic-Tac-Toe: Put A1` to `Tic-Tac-Toe: Put C3`
- Reversi: `Reversi: Put A1` to `Reversi: Put H8`
- Number Guess: `Number Guess: 1` to `Number Guess: 100`

</details>

---

Inspired by [@marcizhu](https://github.com/marcizhu/marcizhu)
