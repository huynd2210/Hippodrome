# 🎯 Hippodrome Solution Explorer

A beautiful, interactive web application to explore the complete database of 415,801 hippodrome puzzle solutions.

## Features

### 🎮 Interactive Board
- Visual 4×4 chess board with animated piece movements
- Step-by-step solution playback with smooth animations
- Highlighted moves and piece transitions
- Goal state visualization (knights in top row)

### 🔍 Exploration Tools
- **Search by ID**: Find any specific configuration (0-415800)
- **Random Explorer**: Discover puzzles randomly
- **Difficulty Filter**: Filter by move count (21-37 moves)
- **Extreme Cases**: View hardest, easiest, fastest, and slowest solutions

### 🎬 Playback Controls
- Play/pause solution animation
- Step forward/backward through solutions
- Jump to first/last step
- Adjustable playback speed (0.2s - 2.0s per step)
- Progress bar with visual feedback

### 📊 Statistics Dashboard
- Complete database statistics
- Move distribution analysis
- Solve time metrics
- Real-time solution information

### ⌨️ Keyboard Shortcuts
- **Space**: Play/Pause
- **←/→ Arrow Keys**: Previous/Next step
- **Home/End**: Jump to first/last step  
- **R**: Random puzzle

## Installation

1. **Install Dependencies**
```bash
cd frontend_explorer
pip install -r requirements.txt
```

2. **Start the Server**
```bash
python app.py
```

3. **Open in Browser**
Navigate to: `http://localhost:5000`

## Requirements

- Python 3.7+
- Flask 2.3+
- Pandas 2.0+
- The complete solution file: `../solutions_csv/configs_0_to_415800_solutions_14t.csv`

## API Endpoints

The backend provides RESTful API endpoints:

- `GET /api/solution/<id>` - Get specific solution
- `GET /api/random` - Get random solution
- `GET /api/search?min_moves=X&max_moves=Y` - Filter solutions
- `GET /api/stats` - Database statistics
- `GET /api/extremes` - Hardest/easiest/fastest/slowest solutions

## Usage

1. **Explore Random Puzzles**: Click "Random Puzzle" to discover interesting configurations
2. **Search Specific IDs**: Enter any ID (0-415800) to view that exact configuration
3. **Filter by Difficulty**: Use the move range sliders to find puzzles of specific difficulty
4. **Watch Solutions**: Use playback controls to see step-by-step solutions
5. **Analyze Extremes**: View the most challenging or easiest puzzles in the database

## Technical Details

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Flask (Python)
- **Data**: 209MB CSV with 415,801 complete solutions
- **Board Representation**: 16-character strings (4×4 grid, row-major)
- **Chess Pieces**: K=King, R=Rook, B=Bishop, N=Knight, x=Empty

## Performance

- **Data Loading**: ~2-3 seconds to load complete database
- **Solution Display**: Instant (<100ms)
- **Search Operations**: Sub-second response times
- **Memory Usage**: ~500MB for complete dataset in memory

This explorer showcases the incredible achievement of solving all 415,801 possible hippodrome configurations with optimal A* search algorithms and multi-threaded processing. 