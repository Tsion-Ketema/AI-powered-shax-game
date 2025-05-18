# AI-Powered Shax (Shah) Game

A GUI-based implementation of **Shax**, a traditional Somali two-player strategy game. This project supports both Human vs AI and AI vs AI gameplay using three AI strategies: **Minimax**, **Monte Carlo Tree Search (MCTS)**, and a **Heuristic-Enhanced Minimax**.

## 🎯 Project Objective

To develop an intelligent Shax-playing agent that:
- Fully follows the traditional rules of the game,
- Plays competitively against human and AI opponents,
- Allows performance comparison between different AI strategies.

## 🧠 AI Strategies

- **MWOR**: Minimax with alpha-beta pruning (no additional rules)  
- **MCTS**: Monte Carlo Tree Search with UCT and 1,000 simulations  
- **MWR**: Minimax with domain-specific heuristics (mill blocking, double-threat creation, loop detection, etc.)

## 🖥️ How to Run

```bash
python main.py
You’ll be prompted to select one of four modes:

MWOR vs MCTS

MWR vs MCTS

Human vs MWR

MWR vs MWOR

📦 Features
Simple and intuitive Tkinter GUI

Three AI strategies with swappable configurations

Game result logging and summary plotting

Modular design for easy maintenance and expansion
