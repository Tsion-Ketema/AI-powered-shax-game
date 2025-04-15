This is an AI powered Shax game, which can be played in a board between two players in a deterministic environment, This project applies techniques such as Minimax and Alpha-Beta Pruning.

# Shax Game Rules

## Overview

Shax is a two-player strategy board game played on a 24-position board. Each player has 12 pieces. The game consists of four distinct phases: Placement, Opening, Movement, and Capture.

## Game Phases

### 1. Placement Phase

- Players take turns placing their pieces on the board.
- The goal is to form a **mill** (three pieces in a row).
- Possible conditions:
  1. One player forms one or more mills.
  2. Both players form mills.
  3. No mills are formed.

### 2. Opening Phase

- Players remove one opponent's piece, turn by turn, based on the Placement phase outcome:
  1. If only one player forms a mill, they remove an opponent's piece first.
  2. If both form mills, the first player to form a mill removes a piece first.
  3. If no mills were formed, the second player of the Placement phase starts.

### 3. Movement Phase

- Players move pieces to adjacent positions.
- Diagonal moves and jumping are not allowed.
- If a player forms a mill, they remove an opponent's piece.
- If a player is blocked, the opponent may move their own pieces strategically to unblock them.

### 4. Capture Phase

- The game ends when a player has only **two pieces left** or **gives up**.

## Winning Conditions

- A player wins when their opponent is reduced to two pieces.
- A player wins if their opponent concedes the game.

Enjoy playing Shax!
