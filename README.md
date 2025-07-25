# Hippodrome Solver 🏇♟️

A high-performance puzzle solver for the **Hippodrome puzzle** - a chess-based puzzle where you must arrange pieces (King, Rook, Bishop, Knight) on a 4x4 board to reach a specific goal state.

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
