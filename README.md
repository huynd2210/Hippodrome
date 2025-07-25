# Hippodrome Solver 🏇♟️

A high-performance puzzle solver for the **Hippodrome puzzle** - a chess-based puzzle where you must arrange pieces (King, Rook, Bishop, Knight) on a 4x4 board to reach a specific goal state.

## 🚀 Quick Start

### 1. **Compile the Solver**
```bash
g++ -std=c++17 -O3 -pthread hippodrome_solver_working.cpp -o solver
```

### 2. **Run the Solver**
```bash
# Solve first 100 configurations with 4 threads (default: top-row target)
./solver 0-99 4

# Solve with first-column target
./solver 0-99 4 first-column

# Solve with custom target positions
./solver 0-99 4 "0,1,4,5"

# Solve all configurations with maximum threads
./solver 0-415800 14
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
