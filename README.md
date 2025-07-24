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

## 📁 Project Structure

```
hippodrome-solver/
├── 🎯 Core Solver
│   ├── hippodrome_solver_working.cpp    # Main multi-threaded solver
│   ├── hippodrome_solver.h              # Header definitions
│   └── filtered_hippodrome_configs.csv  # Input puzzle configurations
│
├── 🌐 Frontend Explorer
│   ├── app.py                          # Flask REST API
│   ├── templates/index.html            # Web interface
│   ├── static/                         # CSS, JS, assets
│   ├── create_database.py              # SQLite database setup
│   └── requirements.txt                # Python dependencies
│
├── 🔧 Utilities
│   ├── visualize_solution.py           # CLI solution visualizer
│   ├── validate_solutions.py           # Solution validator
│   ├── validate_all_solutions.py       # Batch validator
│   └── demo_visualizer.py              # Demo script
│
├── 🧪 Tests
│   └── tests/                          # Unit tests
│
└── 📚 Documentation
    ├── README_visualizer.md            # Visualizer guide
    ├── README_multithreaded_solver.md  # Solver documentation
    ├── README_range_solver.md          # Range processing guide
    └── README_solution_validator.md    # Validator documentation
```

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

### **Solution Validation**
```bash
# Validate a single solution file
python validate_solutions.py solutions.csv

# Validate all solution files in a directory
python validate_all_solutions.py solutions_directory/
```

## 🏗️ Technical Details

### **Algorithm**: A* Search
- **Heuristic**: Manhattan distance + piece-specific movement costs
- **State space**: 4x4 board with 4 piece types
- **Goal state**: All non-Knight pieces in bottom-left 3x3 area

### **Performance**
- **Speed**: ~8.84ms average per configuration
- **Memory**: Efficient state representation
- **Scalability**: Multi-threaded processing
- **Database**: SQLite for O(1) solution lookup

### **Web Technology Stack**
- **Backend**: Flask + SQLite
- **Frontend**: Vanilla JavaScript + CSS3
- **Graphics**: SVG chess pieces (Lichess style)
- **Responsive**: Works on desktop and mobile

## 🎨 Web Interface Features

### **Board Editor**
- Click squares to place/remove pieces
- Piece palette: King, Rook, Bishop, Knight, Empty
- Real-time board state validation
- Search database for matching configurations

### **Solution Playback**
- ▶️ Play/Pause controls
- ⏭️ Step forward/backward
- 🎚️ Speed slider (0.5x - 4x)
- 📊 Progress bar
- 🔄 Auto-replay

### **Database Explorer**
- 🎲 Random puzzle generator
- 📊 Statistics dashboard
- 🔍 Search by configuration
- 💾 415,801+ solved puzzles

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Test specific validator
python test_validator.py

# Test web API
cd frontend_explorer
python test_api.py
```

## 📊 Results

The solver has successfully processed **415,801 unique Hippodrome configurations**:
- ✅ **Solvable**: ~70% of configurations
- ❌ **Unsolvable**: ~30% of configurations  
- 📈 **Solution lengths**: 21-35 moves typically
- ⚡ **Processing time**: ~1 hour for all configurations (14 threads)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Chess piece graphics inspired by [Lichess](https://lichess.org)
- A* algorithm implementation optimized for chess piece movements
- Multi-threading approach for high-performance puzzle solving

---

**Made with ❤️ for puzzle enthusiasts and chess lovers!** 🏇♟️

[⭐ Star this repo](https://github.com/yourusername/hippodrome-solver) | [🐛 Report Issues](https://github.com/yourusername/hippodrome-solver/issues) | [💡 Request Features](https://github.com/yourusername/hippodrome-solver/issues)

