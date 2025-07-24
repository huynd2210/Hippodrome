# 🏇 Hippodrome Solution Visualizer

A Python tool to visualize step-by-step solutions for the Hippodrome puzzle, showing how pieces move to achieve the goal state where all knights (N) are in the top row.

## 📁 Files Created

- **`visualize_solution.py`** - Main interactive visualizer
- **`demo_visualizer.py`** - Automated demo showing first 5 steps
- **`README_visualizer.md`** - This usage guide

## 🚀 Quick Start

### Option 1: Interactive Visualization
```bash
# View all solutions interactively
python visualize_solution.py

# View specific config ID (e.g., config 0)
python visualize_solution.py solutions_csv/first_5_solutions.csv 0

# View from custom CSV file
python visualize_solution.py path/to/your/solutions.csv
```

### Option 2: Auto Demo (First 5 Steps)
```bash
# Quick demo of the first solution
python demo_visualizer.py
```

## 🎮 Interactive Controls

When running the interactive visualizer:

- **Enter** - Show next step
- **`q`** - Quit visualization
- **`a`** - Switch to auto-play mode (0.5s between steps)
- **`y/n/q`** - Continue to next solution when viewing multiple configs

## 📊 What You'll See

### Board Visualization
```
=== Step 3/29 ===
┌───┬───┬───┬───┐
│ K │ B │ R │ K │
├───┼───┼───┼───┤
│ B │ R │ R │ K │
├───┼───┼───┼───┤
│ K │   │ B │ N │    ← Empty space shows as blank
├───┼───┼───┼───┤
│ N │ R │ N │ N │
└───┴───┴───┴───┘
```

### Piece Legend
- **K** = King
- **R** = Rook  
- **B** = Bishop
- **N** = Knight (goal: get all N pieces to top row)
- **` `** = Empty space (represented as 'x' in data, displayed as blank)

### Solution Information
- **Config ID** - Puzzle configuration number
- **Moves** - Total number of moves in solution
- **Time** - Solver execution time in milliseconds
- **Step Progress** - Current step / total steps

## 🎯 Example Output

```
🏇 Hippodrome Solution Visualizer 🏇
========================================
Reading solutions from: solutions_csv/first_5_solutions.csv
Showing only config ID: 0

============================================================
SOLUTION VISUALIZATION - Config ID: 0
Moves: 28 | Time: 10.76ms
============================================================

=== Step 1/29 ===
┌───┬───┬───┬───┐
│ K │ B │ R │ K │
├───┼───┼───┼───┤
│ B │ R │ R │ K │
├───┼───┼───┼───┤
│ K │ R │ B │   │
├───┼───┼───┼───┤
│ N │ N │ N │ N │
└───┴───┴───┴───┘

Press Enter for next step, 'q' to quit, 'a' for auto-play:
```

## ⚙️ Features

### ✅ Interactive Mode
- Step through solutions manually
- Full control over pacing
- Quit anytime or switch to auto-play

### ✅ Auto-Play Mode  
- Automatic progression (0.5s delays)
- Perfect for demos or quick viewing

### ✅ Selective Viewing
- View all solutions or specific config IDs
- Choose which CSV file to process

### ✅ Goal Detection
- Automatically detects when goal is achieved
- Shows celebration message: "🎉 GOAL ACHIEVED!"

### ✅ Error Handling
- Validates CSV file format
- Handles missing files gracefully
- Checks board state format (16 characters)

## 📝 CSV Format Expected

The visualizer expects CSV files with these columns:
- **ID** - Configuration ID
- **Initial Board** - 16-character board state string
- **Solution Path** - Semicolon-separated board states
- **Moves** - Number of moves (-1 for no solution)
- **Time (ms)** - Solver execution time

## 🔧 Customization

You can modify the visualization by editing:

- **Board symbols** in `print_board()` function
- **Step delays** in auto-play mode
- **Display formatting** for headers and borders
- **Interactive prompts** and messages

## 💡 Tips

1. **Large solutions**: Use auto-play mode for solutions with many moves
2. **Multiple configs**: View all solutions, then select specific ones for detailed analysis
3. **Custom CSV**: Point to any compatible CSV file from your solver runs
4. **Goal tracking**: Watch for the "🎉 GOAL ACHIEVED!" message when knights reach the top row

## 🛠️ Requirements

- Python 3.6+ (uses f-strings and type hints)
- Standard library only (no external dependencies)
- CSV files from the hippodrome solver

## 🎬 Demo

Run `python demo_visualizer.py` for a quick 5-step preview of how the visualizer works!

---

*Happy puzzle solving! 🧩✨* 