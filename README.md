# Hippodrome Solver 🏇♟️

A high-performance puzzle solver for the **Hippodrome puzzle** - a chess-based puzzle where knights must be moved to reach specific target positions on a 4x4 board containing various chess pieces as obstacles.

## 🧩 The Puzzle

The Hippodrome puzzle features:
- A 4x4 board with 4 knights (N) and various obstacle pieces (Kings K, Rooks R, Bishops B)
- One empty square (x) that allows movement
- Goal: Move all 4 knights to specific target positions
- Knights move in standard chess L-shapes, other pieces slide to adjacent squares

## 🚀 Quick Start

### 1. **Compile the Solver**
```bash
g++ -std=c++17 -O3 -pthread hippodrome_solver_working.cpp -o solver
# Or use the Makefile:
make
```
### 2. **Start the Web Explorer**
```bash
cd frontend_explorer
pip install -r requirements.txt

# Create target-specific databases from solution CSV files
python create_target_databases.py ../solutions_csv/hippodrome_solutions_og.csv
python create_target_databases.py ../solutions_csv/hippodrome_solutions_first_column.csv
# ... repeat for other target CSV files

# Start the web server
python app.py
```

Open http://localhost:5000 in your browser! 🎉

## 💻 Usage Examples

### **Solver Command Line**
```bash
# Basic usage (default: first 5 configs, top-row target)
./solver

# Solve specific range with threads
./solver 1000-2000 8

# Process all configurations with different targets
./solver 0-415800 12 top-row          # Knights must reach positions 0,1,2,3
./solver 0-415800 12 bottom-row       # Knights must reach positions 12,13,14,15
./solver 0-415800 12 first-column     # Knights must reach positions 0,4,8,12
./solver 0-415800 12 last-column      # Knights must reach positions 3,7,11,15
./solver 0-415800 12 "0,1,4,5"        # Custom target positions

# Single configuration with specific target
./solver 42 1 first-column
```

### **Target Options**
- **`top-row`** (default): Knights must reach the top row (positions 0,1,2,3)
- **`bottom-row`**: Knights must reach the bottom row (positions 12,13,14,15) 
- **`first-column`**: Knights must reach the first column (positions 0,4,8,12)
- **`last-column`**: Knights must reach the last column (positions 3,7,11,15)
- **Custom positions**: Specify 4 exact positions like `"0,1,4,5"` or `"2,6,10,14"`

### **Board Position Layout**
```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

## 🔧 Technical Details

### Algorithm
- **A* Search**: Optimal pathfinding with admissible heuristic
- **Heuristic**: BFS-based minimum knight distance to target positions
- **Multi-threading**: Parallel processing of configurations for performance
- **State Representation**: 16-character string (e.g., "RKKKBBBBRRxNNNNN")

### Web Interface Features
- Interactive board visualization
- Step-by-step solution playback
- Multiple playback speeds (0.5x to 4x)
- Target position highlighting
- Solution statistics and distribution

## 🛠️ Building from Source

### Requirements
- C++17 compatible compiler (g++, clang++)
- Python 3.7+
- SQLite3

### Compilation Options
```bash
# Debug build
g++ -std=c++17 -g hippodrome_solver_working.cpp -o solver_debug

# Release build with maximum optimization
g++ -std=c++17 -O3 -march=native -pthread hippodrome_solver_working.cpp -o solver

# Using Makefile
make          # Standard build
make clean    # Clean build artifacts
```

## 🎯 Target Configurations in Frontend

The web interface supports additional targets not available in the C++ solver:
- **`center`**: Knights must reach center squares (5,6,9,10)
- **`corners`**: Knights must reach corner squares (0,3,12,15)

These require pre-computed solution CSV files in the `solutions_csv/` directory.

## 📝 Notes

- The solver uses lowercase 'x' to represent empty squares
- Board states are represented as 16-character strings in row-major order
- The web interface automatically replaces spaces with 'x' in board representations
- Solution paths are stored as semicolon-separated board states
- Since there are only 1 available space, and no captures are allowed, this means that the queen functions identically as kings. Thus we treat queens as kings in order to reduce the total amount of board configurations down to just 415k.
