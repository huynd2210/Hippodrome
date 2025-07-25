from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import random
import json
from functools import lru_cache

app = Flask(__name__)
CORS(app)

# Lazy loading configuration
TARGETS_INDEX_DB = "targets_index.db"
DATABASE_CACHE = {}  # Cache database connections

def get_targets_index():
    """Get the lightweight targets index"""
    if not os.path.exists(TARGETS_INDEX_DB):
        raise FileNotFoundError(f"Targets index not found: {TARGETS_INDEX_DB}")
    
    conn = sqlite3.connect(TARGETS_INDEX_DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_target_database(target_name):
    """Get database connection for a specific target (with caching)"""
    if target_name in DATABASE_CACHE:
        return DATABASE_CACHE[target_name]
    
    # Get database filename from targets index
    index_conn = get_targets_index()
    cursor = index_conn.cursor()
    cursor.execute('SELECT database_file FROM targets WHERE name = ?', (target_name,))
    result = cursor.fetchone()
    index_conn.close()
    
    if not result:
        raise FileNotFoundError(f"No database found for target: {target_name}")
    
    db_file = result['database_file']
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"Database file not found: {db_file}")
    
    # Create connection and cache it
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    DATABASE_CACHE[target_name] = conn
    
    return conn

def parse_solution_path(solution_path_str):
    """Parse semicolon-separated solution path into list of board states"""
    if not solution_path_str:
        return []
    return solution_path_str.split(';')

@app.route('/')
def index():
    """Serve the main application page - NO database operations here"""
    return render_template('index_lazy.html')

@app.route('/api/targets')
def get_targets():
    """ONLY called when user clicks 'Load Targets' - not automatically"""
    try:
        conn = get_targets_index()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, positions, description, total_solutions FROM targets ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        targets = []
        for row in rows:
            targets.append({
                'name': row['name'],
                'positions': [int(x) for x in row['positions'].split(',')],
                'description': row['description'],
                'total_solutions': row['total_solutions']
            })
        
        return jsonify({'targets': targets})
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/solution/<int:config_id>')
def get_solution(config_id):
    """ONLY called when user searches for a specific solution"""
    target = request.args.get('target', 'first-column')
    
    try:
        conn = get_target_database(target)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, initial_board, solution_path, moves, time_ms FROM solutions WHERE id = ?',
            (config_id,)
        )
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': f'Solution not found for ID {config_id} with target {target}'}), 404
        
        # Get target info from metadata
        cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_positions',))
        target_positions = [int(x) for x in cursor.fetchone()['value'].split(',')]
        
        solution_path = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
            'target_name': target,
            'target_positions': target_positions,
            'initial_board': row['initial_board'],
            'solution_path': solution_path,
            'moves': row['moves'],
            'time_ms': row['time_ms'],
            'total_steps': len(solution_path)
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/random')
def get_random_solution():
    """ONLY called when user clicks 'Random Puzzle'"""
    target = request.args.get('target', 'first-column')
    
    try:
        conn = get_target_database(target)
        cursor = conn.cursor()
        
        # Get a random solution for the specified target
        cursor.execute(
            'SELECT id, initial_board, solution_path, moves, time_ms FROM solutions ORDER BY RANDOM() LIMIT 1'
        )
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': f'No solutions found for target {target}'}), 404
        
        # Get target info from metadata
        cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_positions',))
        target_positions = [int(x) for x in cursor.fetchone()['value'].split(',')]
        
        solution_path = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
            'target_name': target,
            'target_positions': target_positions,
            'initial_board': row['initial_board'],
            'solution_path': solution_path,
            'moves': row['moves'],
            'time_ms': row['time_ms'],
            'total_steps': len(solution_path)
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/search')
def search_solutions():
    """Search solutions with filters for a specific target"""
    target = request.args.get('target', 'top-row')
    min_moves = request.args.get('min_moves', type=int)
    max_moves = request.args.get('max_moves', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    try:
        conn = get_target_database(target)
        cursor = conn.cursor()
        
        # Build query with filters
        query = 'SELECT id, initial_board, moves, time_ms FROM solutions WHERE 1=1'
        params = []
        
        if min_moves is not None:
            query += ' AND moves >= ?'
            params.append(min_moves)
        
        if max_moves is not None:
            query += ' AND moves <= ?'
            params.append(max_moves)
        
        # Get total count matching criteria
        count_query = query.replace('SELECT id, initial_board, moves, time_ms FROM solutions', 'SELECT COUNT(*) FROM solutions')
        cursor.execute(count_query, params)
        total_found = cursor.fetchone()[0]
        
        # Add random ordering and limit
        query += ' ORDER BY RANDOM() LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'initial_board': row['initial_board'],
                'moves': row['moves'],
                'time_ms': row['time_ms']
            })
        
        return jsonify({
            'results': results,
            'total_found': total_found,
            'showing': len(results),
            'target': target
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/stats')
def get_statistics():
    """ONLY called when user requests statistics"""
    target = request.args.get('target', 'first-column')
    
    try:
        conn = get_target_database(target)
        cursor = conn.cursor()
        
        # Get basic statistics for the target
        cursor.execute('SELECT COUNT(*) FROM solutions')
        total_solutions = cursor.fetchone()[0]
        
        if total_solutions == 0:
            return jsonify({'error': f'No solutions found for target {target}'}), 404
        
        cursor.execute('SELECT MIN(moves), MAX(moves), AVG(moves) FROM solutions WHERE moves > 0')
        result = cursor.fetchone()
        min_moves, max_moves, avg_moves = result[0], result[1], result[2]
        
        # Calculate median moves (simplified approach)
        cursor.execute('SELECT moves FROM solutions WHERE moves > 0 ORDER BY moves LIMIT 1 OFFSET (SELECT COUNT(*) FROM solutions WHERE moves > 0) / 2')
        median_result = cursor.fetchone()
        median_moves = median_result[0] if median_result else avg_moves
        
        cursor.execute('SELECT MIN(time_ms), MAX(time_ms), AVG(time_ms) FROM solutions')
        time_result = cursor.fetchone()
        min_time, max_time, avg_time = time_result[0], time_result[1], time_result[2]
        
        # Get move distribution (top 20 most common)
        cursor.execute('SELECT moves, COUNT(*) FROM solutions GROUP BY moves ORDER BY COUNT(*) DESC LIMIT 20')
        move_distribution = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # Get target info from metadata
        cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_positions',))
        target_positions = [int(x) for x in cursor.fetchone()['value'].split(',')]
        
        cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_description',))
        target_description = cursor.fetchone()['value']
        
        stats = {
            'target': target,
            'target_positions': target_positions,
            'target_description': target_description,
            'total_solutions': total_solutions,
            'move_stats': {
                'min': min_moves,
                'max': max_moves,
                'mean': avg_moves,
                'median': median_moves
            },
            'time_stats': {
                'min': min_time,
                'max': max_time,
                'mean': avg_time
            },
            'move_distribution': move_distribution
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/extremes')
def get_extreme_solutions():
    """Get the most interesting solutions for a specific target"""
    target = request.args.get('target', 'top-row')
    
    try:
        conn = get_target_database(target)
        cursor = conn.cursor()
        
        # Get extreme cases for the target
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions WHERE moves > 0 ORDER BY moves DESC LIMIT 1')
        hardest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions WHERE moves > 0 ORDER BY moves ASC LIMIT 1')
        easiest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions ORDER BY time_ms ASC LIMIT 1')
        fastest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions ORDER BY time_ms DESC LIMIT 1')
        slowest = cursor.fetchone()
        
        def format_solution(row):
            return {
                'id': row['id'],
                'initial_board': row['initial_board'],
                'moves': row['moves'],
                'time_ms': row['time_ms']
            } if row else None
        
        return jsonify({
            'target': target,
            'hardest': format_solution(hardest),
            'easiest': format_solution(easiest),
            'fastest': format_solution(fastest),
            'slowest': format_solution(slowest)
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint - NO database operations"""
    return jsonify({
        'status': 'ready',
        'database': 'on_demand_only',
        'message': 'Databases loaded only when requested'
    })

@app.route('/api/search_by_board', methods=['POST'])
def search_by_board():
    """ONLY called when user searches by board configuration"""
    try:
        data = request.get_json()
        board_state = data.get('board_state')
        target = data.get('target', 'first-column')
        
        if not board_state:
            return jsonify({'error': 'board_state is required'}), 400
            
        if len(board_state) != 16:
            return jsonify({'error': 'board_state must be exactly 16 characters'}), 400
        
        conn = get_target_database(target)
        cursor = conn.cursor()
        
        # Search for exact matches for the specified target
        cursor.execute(
            'SELECT id, initial_board, moves FROM solutions WHERE initial_board = ? LIMIT 10', 
            (board_state,)
        )
        rows = cursor.fetchall()
        
        # Filter out unsolvable configurations
        results = []
        for row in rows:
            if row['moves'] != -1:
                results.append({
                    'id': row['id'],
                    'initial_board': row['initial_board'],
                    'moves': row['moves']
                })
        
        return jsonify({
            'results': results,
            'total_found': len(results),
            'search_board': board_state,
            'target': target,
            'message': f'Found {len(results)} solvable configuration(s) for {target} target' if results else f'No solvable configurations found for {target} target'
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/compare_targets/<int:config_id>')
def compare_targets(config_id):
    """Compare solutions for the same configuration across different targets"""
    try:
        # Get all available targets first
        index_conn = get_targets_index()
        cursor = index_conn.cursor()
        cursor.execute('SELECT name FROM targets')
        available_targets = [row['name'] for row in cursor.fetchall()]
        index_conn.close()
        
        comparisons = []
        
        for target in available_targets:
            try:
                conn = get_target_database(target)
                target_cursor = conn.cursor()
                
                target_cursor.execute(
                    'SELECT moves, time_ms FROM solutions WHERE id = ?', (config_id,)
                )
                result = target_cursor.fetchone()
                
                # Get target positions
                target_cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_positions',))
                positions_result = target_cursor.fetchone()
                
                if result and positions_result:
                    target_positions = [int(x) for x in positions_result['value'].split(',')]
                    comparisons.append({
                        'target_name': target,
                        'target_positions': target_positions,
                        'moves': result['moves'],
                        'time_ms': result['time_ms']
                    })
                
            except Exception as e:
                # Target database might not exist or config might not be in that target
                continue
        
        if not comparisons:
            return jsonify({'error': f'Configuration {config_id} not found in any target'}), 404
        
        return jsonify({
            'config_id': config_id,
            'comparisons': comparisons,
            'total_targets': len(comparisons)
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎯 On-Demand Lazy-Loading Hippodrome Explorer")
    print("=" * 55)
    print("✅ ZERO database operations on startup!")
    print("🔄 Databases loaded ONLY when user requests:")
    print("   • Click 'Load Targets' → loads targets index")
    print("   • Search for solution → loads target database")
    print("   • Click random puzzle → loads target database")
    print("🚀 Starting at http://localhost:5000")
    print("⚡ INSTANT page loading guaranteed!")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 