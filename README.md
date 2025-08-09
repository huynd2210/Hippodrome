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

# Start the web server (uses compact binary files by default)
python app.py
```

Open http://localhost:5000 in your browser! 🎉

**Note:** The frontend now uses compact binary files (~14-19MB each) instead of large SQLite databases (~130MB each) for much faster loading and deployment.

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
- **`center`**: Knights must reach center squares (5,6,9,10)
- **`corners`**: Knights must reach corner squares (0,3,12,15)
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

### Solution Encoding (New!)
The solver now uses a compact binary format for efficient storage and loading:

- **Bitboard representation**: 8×16-bit integers for board state encoding
- **Szudzik pairing**: Perfect hash function for board state identification
- **Compact moves**: 1 byte per move (4 bits for 'from', 4 bits for 'to')
- **Binary format**: Custom `.bin` files with 85-90% size reduction vs CSV

**File sizes:**
- **Original CSV**: ~130MB per target
- **Binary format**: ~14-19MB per target
- **Compression ratio**: ~7:1 for move data, ~2:1 overall

### Web Interface Features
- Interactive board visualization
- Step-by-step solution playback
- Multiple playback speeds (0.5x to 4x)
- Target position highlighting
- Solution statistics and distribution
- **New**: Direct binary file loading (faster startup)

## 🛠️ Building from Source

### Requirements
- C++17 compatible compiler (g++, clang++)
- Python 3.7+
- SQLite3 (optional, for legacy database mode)

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

## 🌐 Cloud Deployment

The application is designed for easy cloud deployment with compact binary files:

### Quick Deploy on Render

1. **Fork this repository**
2. **Create a new Web Service on Render**
3. **Configure the service:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd frontend_explorer && gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment Variables**:
     - `HIPPO_SOURCE=bin` (uses binary files)
     - `BIN_URL_TOP_ROW=https://your-storage/hippodrome_solutions_og.bin`
     - `BIN_URL_FIRST_COLUMN=https://your-storage/hippodrome_solutions_first_column.bin`
     - `BIN_URL_LAST_COLUMN=https://your-storage/hippodrome_solutions_last_column.bin`
     - `BIN_URL_CORNERS=https://your-storage/hippodrome_solutions_corners.bin`
     - `BIN_URL_CENTER=https://your-storage/hippodrome_solutions_center.bin`

4. **Upload binary files** to object storage (Cloudflare R2, AWS S3, etc.)
5. **Deploy!**

### Alternative: Database-backed Deployment

If you prefer the legacy SQLite approach:
- Set `HIPPO_SOURCE=db`
- Upload SQLite database files instead of binary files
- Use `DB_URL_*` environment variables

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📁 Project Structure

```
hippodrome-solver-github/
├── hippodrome_solver_working.cpp    # Main C++ solver
├── frontend_explorer/
│   ├── app.py                       # Unified Flask application
│   ├── static/                      # CSS, JS, images
│   └── templates/                   # HTML templates
├── encoded_solutions/               # Compact binary files
│   ├── hippodrome_solutions_og.bin
│   ├── hippodrome_solutions_center.bin
│   └── ...
├── utils/                           # Python utilities
│   ├── encode_binary.py            # CSV to binary converter
│   ├── decode_and_verify.py        # Binary verification tool
│   └── transform_solutions.py      # Solution transformation
├── solutions_csv/                   # Original CSV files
├── render.yaml                      # Render deployment config
├── Procfile                         # Heroku deployment config
└── requirements.txt                 # Python dependencies
```

## 🎯 Target Configurations

The web interface supports all major targets:

- **`top-row`**: Knights must reach the top row (positions 0,1,2,3)
- **`first-column`**: Knights must reach the first column (positions 0,4,8,12)
- **`last-column`**: Knights must reach the last column (positions 3,7,11,15)
- **`center`**: Knights must reach center squares (5,6,9,10)
- **`corners`**: Knights must reach corner squares (0,3,12,15)

## 📝 Notes

- The solver uses lowercase 'x' to represent empty squares
- Board states are represented as 16-character strings in row-major order
- The web interface automatically replaces spaces with 'x' in board representations
- Solution paths are stored as semicolon-separated board states
- Since there are only 1 available space, and no captures are allowed, this means that the queen functions identically as kings. Thus we treat queens as kings in order to reduce the total amount of board configurations down to just 415k.

## 🔄 Recent Updates

- **Binary encoding**: Implemented compact binary format for 85-90% size reduction
- **Unified frontend**: Single Flask app supporting both binary and database backends
- **Cloud deployment**: Optimized for Render, Heroku, and other cloud platforms
- **Performance**: Faster loading with in-memory binary indexing
- **Cleanup**: Removed redundant files and organized utilities

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
