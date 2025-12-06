# Hippodrome
This repository contains the code and solution to every possible configuration for Hippodrome. 

Interactive Demo: https://hippodrome.onrender.com/

<img width="732" height="411" alt="image" src="https://github.com/user-attachments/assets/ee2a7c10-7c90-4da6-8986-d42625f2e9e8" />


For more information on the chess-puzzle Hippodrome, visit: https://www.chessvariants.com/solitaire.dir/hippodrome.html

The Hippodrome puzzle features:
- A 4x4 board with 4 knights (N) and various obstacle pieces (Kings K, Rooks R, Bishops B)
- One empty square (x) that allows movement
- Goal: Move all 4 knights to specific target positions
- Knights move in standard chess L-shapes, other pieces slide to adjacent squares

Note: In the original puzzle, there are both kings and queens, but in this repo, only kings are present. This is because in Hippodrome, there are no captures, and there is only 1 available empty spot on the board at all times. Therefore we consider kings as queens when solving, this reduces the amount of possible configurations.

## Quick Start

### 1. **Compile the Solver**
```bash
g++ -std=c++17 -O3 -pthread hippodrome_solver_working.cpp -o solver
# Or use the Makefile:
make
```

### 2. **Start the Web Explorer**
```bash
pip install -r requirements.txt
cd frontend_explorer

# Start the web server (uses compact binary files by default)
python app.py
```

Open http://localhost:5000 in your browser

## Usage Examples

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
- **`center`**: Knights must reach center squares (5,6,9,10)
- **`corners`**: Knights must reach corner squares (0,3,12,15)
- **Custom positions**: Specify 4 exact positions like `"0,1,4,5"` or `"2,6,10,14"`



## Technical Details

### Algorithm
- **A* Search**: Optimal pathfinding with admissible heuristic
- **Heuristic**: BFS-based minimum knight distance to target positions

### Solution Encoding
### **Board Position Layout**
```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```
Each puzzle configuration is encoded as follow to minimize space:
- 8×16-bit integers for board state encoding
- Perfect hash function for board state identification using Szudzik pairing
- 1 byte per move (4 bits for 'from', 4 bits for 'to')
- Stored as .bin
## Building from Source

### Requirements
- C++17 compatible compiler (g++, clang++)
- Python 3.7+

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
## Target Configurations

The web interface supports all major targets:

- **`top-row`**: Knights must reach the top row (positions 0,1,2,3)
- **`first-column`**: Knights must reach the first column (positions 0,4,8,12)
- **`last-column`**: Knights must reach the last column (positions 3,7,11,15)
- **`center`**: Knights must reach center squares (5,6,9,10)
- **`corners`**: Knights must reach corner squares (0,3,12,15)
