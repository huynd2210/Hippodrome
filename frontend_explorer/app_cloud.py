from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import random
import json
import urllib.request
import tempfile
import hashlib
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Cache directory for downloaded databases
CACHE_DIR = Path(tempfile.gettempdir()) / 'hippodrome_cache'
CACHE_DIR.mkdir(exist_ok=True)

# Database URLs from environment variables or defaults
DB_URLS = {
    'targets_index': os.environ.get('DB_URL_TARGETS_INDEX', ''),
    'top-row': os.environ.get('DB_URL_TOP_ROW', ''),
    'first-column': os.environ.get('DB_URL_FIRST_COLUMN', ''),
    'last-column': os.environ.get('DB_URL_LAST_COLUMN', ''),
    'corners': os.environ.get('DB_URL_CORNERS', ''),
    'center': os.environ.get('DB_URL_CENTER', '')
}

def get_db_path(db_name):
    """Get database path, downloading from URL if needed"""
    # First check if local file exists
    local_names = {
        'targets_index': 'targets_index.db',
        'top-row': 'hippodrome_top_row.db',
        'first-column': 'hippodrome_first_column.db',
        'last-column': 'hippodrome_last_column.db',
        'corners': 'hippodrome_corners.db',
        'center': 'hippodrome_center.db'
    }
    
    local_file = local_names.get(db_name, f'hippodrome_{db_name}.db')
    if os.path.exists(local_file):
        return local_file
    
    # Check if we have a URL for this database
    db_url = DB_URLS.get(db_name, '')
    if not db_url:
        raise FileNotFoundError(f"No database found for {db_name}")
    
    # Check cache
    url_hash = hashlib.md5(db_url.encode()).hexdigest()
    cache_path = CACHE_DIR / f"{db_name}_{url_hash}.db"
    
    if cache_path.exists():
        print(f"Using cached {db_name} database")
        return str(cache_path)
    
    # Download database
    print(f"Downloading {db_name} database from {db_url[:50]}...")
    try:
        urllib.request.urlretrieve(db_url, cache_path)
        print(f"Successfully downloaded {db_name} database")
        return str(cache_path)
    except Exception as e:
        raise Exception(f"Failed to download {db_name} database: {str(e)}")

def get_target_db_connection(target_name):
    """Get a database connection for a specific target"""
    db_path = get_db_path(target_name)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_targets_index():
    """Get the targets index database connection"""
    db_path = get_db_path('targets_index')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def parse_solution_path(solution_path_str):
    """Parse semicolon-separated solution path into list of board states"""
    if not solution_path_str:
        return []
    return solution_path_str.split(';')

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/targets')
def get_targets():
    """Get all available targets"""
    try:
        # Return predefined targets if we can't access the index
        default_targets = [
            {'name': 'top-row', 'positions': '0,1,2,3'},
            {'name': 'first-column', 'positions': '0,4,8,12'},
            {'name': 'last-column', 'positions': '3,7,11,15'},
            {'name': 'corners', 'positions': '0,3,12,15'},
            {'name': 'center', 'positions': '5,6,9,10'}
        ]
        
        try:
            conn = get_targets_index()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM targets ORDER BY name')
            targets = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return jsonify(targets)
        except:
            # Return default targets if index is not available
            return jsonify(default_targets)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solution/<int:config_id>')
def get_solution(config_id):
    """Get a specific solution by configuration ID"""
    target = request.args.get('target', 'top-row')
    
    try:
        conn = get_target_db_connection(target)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, initial_board, solution_path, moves, time_ms FROM solutions WHERE id = ?',
            (config_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': f'Solution not found for config {config_id} with target {target}'}), 404
        
        # Parse the solution path
        solution_steps = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
            'initial_board': row['initial_board'],
            'solution_path': solution_steps,
            'moves': row['moves'],
            'time_ms': row['time_ms'],
            'target': target
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/random')
def get_random_solution():
    """Get a random solution"""
    target = request.args.get('target', 'top-row') 
    
    try:
        conn = get_target_db_connection(target)
        cursor = conn.cursor()
        
        # Get random solution
        cursor.execute('SELECT id, initial_board, solution_path, moves, time_ms FROM solutions ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': f'No solutions found for target {target}'}), 404
        
        # Parse the solution path
        solution_steps = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
            'initial_board': row['initial_board'],
            'solution_path': solution_steps,
            'moves': row['moves'],
            'time_ms': row['time_ms'],
            'target': target
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_solutions():
    """Search solutions by criteria"""
    target = request.args.get('target', 'top-row')
    min_moves = request.args.get('min_moves', type=int)
    max_moves = request.args.get('max_moves', type=int)
    limit = min(request.args.get('limit', 10, type=int), 100)  # Cap at 100
    
    try:
        conn = get_target_db_connection(target)
        cursor = conn.cursor()
        
        query = 'SELECT id, initial_board, moves, time_ms FROM solutions WHERE 1=1'
        params = []
        
        if min_moves is not None:
            query += ' AND moves >= ?'
            params.append(min_moves)
        
        if max_moves is not None:
            query += ' AND moves <= ?'
            params.append(max_moves)
        
        query += ' ORDER BY moves ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_statistics():
    """Get database statistics"""
    target = request.args.get('target', 'top-row')
    
    try:
        conn = get_target_db_connection(target)
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute('SELECT COUNT(*) as total FROM solutions')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT AVG(moves) as avg_moves, MIN(moves) as min_moves, MAX(moves) as max_moves FROM solutions')
        moves_stats = cursor.fetchone()
        
        cursor.execute('SELECT AVG(time_ms) as avg_time FROM solutions')
        time_stats = cursor.fetchone()
        
        # Move distribution
        cursor.execute('SELECT moves, COUNT(*) as count FROM solutions GROUP BY moves ORDER BY moves')
        move_distribution = [{'moves': row['moves'], 'count': row['count']} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'target': target,
            'total_solutions': total,
            'avg_moves': round(moves_stats['avg_moves'], 2),
            'min_moves': moves_stats['min_moves'],
            'max_moves': moves_stats['max_moves'],
            'avg_time_ms': round(time_stats['avg_time'], 2),
            'move_distribution': move_distribution
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_by_board')
def search_by_board():
    """Search for solutions by initial board state"""
    board_state = request.args.get('board', '')
    target = request.args.get('target', 'top-row')
    
    if len(board_state) != 16:
        return jsonify({'error': 'Board state must be exactly 16 characters'}), 400
    
    try:
        conn = get_target_db_connection(target)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, initial_board, solution_path, moves, time_ms FROM solutions WHERE initial_board = ?',
            (board_state,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': f'No solution found for this board configuration with target {target}'}), 404
        
        # Parse the solution path
        solution_steps = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
            'initial_board': row['initial_board'],
            'solution_path': solution_steps,
            'moves': row['moves'],
            'time_ms': row['time_ms'],
            'target': target
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ready'})

if __name__ == '__main__':
    print("🎯 Hippodrome Explorer (Cloud Edition) starting...")
    print("📡 Will download databases from URLs if not found locally")
    
    # Use PORT from environment if available (for cloud deployment)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
