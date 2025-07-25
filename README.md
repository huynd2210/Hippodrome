# Hippodrome Solver 🏇♟️

A high-performance puzzle solver for the **Hippodrome puzzle** - a chess-based puzzle where you must arrange pieces (King, Rook, Bishop, Knight) on a 4x4 board to reach a specific goal state.

![Demo](https://img.shields.io/badge/Demo-Live%20Frontend-brightgreen)
![C++](https://img.shields.io/badge/C%2B%2B-Solver-blue)
![Python](https://img.shields.io/badge/Python-Tools-yellow)
![Web](https://img.shields.io/badge/Web-Explorer-orange)

## 🎯 Features

### 🚀 Core Solver
- **Multi-threaded C++ solver** using A* search algorithm
- **Range processing** - solve specific configuration ranges
- **High performance** - processes 415,801 configurations efficiently
- **Knight heuristics** - optimized pathfinding for chess piece movements

### 🎮 Interactive Web Explorer
- **Live solution playback** with step-by-step visualization  
- **Interactive board editor** - place pieces and search for solutions
- **Lichess-style chess pieces** with beautiful SVG graphics
- **SQLite database** for fast solution retrieval
- **Speed controls** - adjust playback speed from 0.5x to 4x
- **Random puzzle generator** for exploration

### 🛠️ Utility Tools
- **Solution visualizer** - command-line step-by-step display
- **Solution validator** - verify correctness of generated solutions
- **Batch processing** - validate all solutions efficiently

## 🚀 Quick Start

### 1. **Compile the Solver**
```bash
g++ -std=c++17 -O3 -pthread hippodrome_solver_working.cpp -o solver
```

### 2. **Run the Solver**
```bash
# Solve first 100 configurations with 4 threads
./solver filtered_hippodrome_configs.csv output.csv 0-99 4

# Solve all configurations with maximum threads
./solver filtered_hippodrome_configs.csv all_solutions.csv 0-415800 14
```

### 3. **Start the Web Explorer**
```bash
cd frontend_explorer
pip install -r requirements.txt

# Create the database (first time only)
python create_database.py path/to/your/solutions.csv

# Start the web server
python app.py
```

Open http://localhost:5000 in your browser! 🎉

## 💻 Usage Examples

### **Solver Command Line**
```bash
# Basic usage
./solver input.csv output.csv

# Solve specific range with threads
./solver input.csv output.csv 1000-2000 8

# Process all configurations
./solver input.csv output.csv 0-415800 12
```

### **Solution Visualization**
```python
from visualize_solution import visualize_solution

# Visualize a solution step by step
moves = "R0→R1,B5→B2,K10→K6,..."
visualize_solution("RRKKBBBRKRKXNNNN", moves)
```