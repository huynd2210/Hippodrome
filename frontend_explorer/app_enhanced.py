from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import random
import json
from functools import lru_cache

app = Flask(__name__)
CORS(app)

# Enhanced database path
DB_PATH = "hippodrome_solutions_enhanced.db"

def get_db_connection():
    """Get a database connection with row factory for dict-like access"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Enhanced database not found: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows dict-like access to rows
    return conn

def parse_solution_path(solution_path_str):
    """Parse semicolon-separated solution path into list of board states"""
    if not solution_path_str:
        return []
    return solution_path_str.split(';')

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index_enhanced.html')

@app.route('/api/targets')
def get_targets():
    """Get all available targets"""
    try:
        conn = get_db_connection()
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
    """Get a specific solution by configuration ID for a target"""
    target = request.args.get('target', 'top-row')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT id, target_name, target_positions, initial_board, solution_path, moves, time_ms 
               FROM solutions WHERE id = ? AND target_name = ?''',
            (config_id, target)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': f'Solution not found for ID {config_id} with target {target}'}), 404
        
        solution_path = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
            'target_name': row['target_name'],
            'target_positions': [int(x) for x in row['target_positions'].split(',')],
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
    """Get a random solution from the database for a specific target"""
    target = request.args.get('target', 'top-row')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get a random solution for the specified target
        cursor.execute(
            '''SELECT id, target_name, target_positions, initial_board, solution_path, moves, time_ms 
               FROM solutions WHERE target_name = ? ORDER BY RANDOM() LIMIT 1''',
            (target,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': f'No solutions found for target {target}'}), 404
        
        solution_path = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
            'target_name': row['target_name'],
            'target_positions': [int(x) for x in row['target_positions'].split(',')],
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = 'SELECT id, initial_board, moves, time_ms FROM solutions WHERE target_name = ?'
        params = [target]
        
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
        conn.close()
        
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
    """Get database statistics for a specific target"""
    target = request.args.get('target', 'top-row')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic statistics for the target
        cursor.execute('SELECT COUNT(*) FROM solutions WHERE target_name = ?', (target,))
        total_solutions = cursor.fetchone()[0]
        
        if total_solutions == 0:
            return jsonify({'error': f'No solutions found for target {target}'}), 404
        
        cursor.execute('SELECT MIN(moves), MAX(moves), AVG(moves) FROM solutions WHERE target_name = ?', (target,))
        min_moves, max_moves, avg_moves = cursor.fetchone()
        
        # Calculate median moves
        cursor.execute('''
            SELECT AVG(moves) FROM (
                SELECT moves FROM solutions WHERE target_name = ? 
                ORDER BY moves 
                LIMIT 2 - (SELECT COUNT(*) FROM solutions WHERE target_name = ?) % 2 
                OFFSET (SELECT (COUNT(*) - 1) / 2 FROM solutions WHERE target_name = ?)
            )''', (target, target, target))
        median_moves = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(time_ms), MAX(time_ms), AVG(time_ms) FROM solutions WHERE target_name = ?', (target,))
        min_time, max_time, avg_time = cursor.fetchone()
        
        # Get move distribution for the target
        cursor.execute('SELECT moves, COUNT(*) FROM solutions WHERE target_name = ? GROUP BY moves ORDER BY moves', (target,))
        move_distribution = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # Get target info
        cursor.execute('SELECT positions, description FROM targets WHERE name = ?', (target,))
        target_info = cursor.fetchone()
        
        conn.close()
        
        stats = {
            'target': target,
            'target_positions': [int(x) for x in target_info['positions'].split(',')],
            'target_description': target_info['description'],
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get extreme cases for the target
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions WHERE target_name = ? ORDER BY moves DESC LIMIT 1', (target,))
        hardest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions WHERE target_name = ? ORDER BY moves ASC LIMIT 1', (target,))
        easiest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions WHERE target_name = ? ORDER BY time_ms ASC LIMIT 1', (target,))
        fastest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions WHERE target_name = ? ORDER BY time_ms DESC LIMIT 1', (target,))
        slowest = cursor.fetchone()
        
        conn.close()
        
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
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM solutions')
        total_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM targets')
        target_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'enhanced_connected',
            'total_solutions': total_count,
            'available_targets': target_count
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/search_by_board', methods=['POST'])
def search_by_board():
    """Search for solutions by board configuration and target"""
    try:
        data = request.get_json()
        board_state = data.get('board_state')
        target = data.get('target', 'top-row')
        
        if not board_state:
            return jsonify({'error': 'board_state is required'}), 400
            
        if len(board_state) != 16:
            return jsonify({'error': 'board_state must be exactly 16 characters'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search for exact matches for the specified target
        cursor.execute(
            'SELECT id, initial_board, moves FROM solutions WHERE initial_board = ? AND target_name = ? LIMIT 10', 
            (board_state, target)
        )
        rows = cursor.fetchall()
        
        # Also check if this board exists for other targets
        cursor.execute(
            'SELECT DISTINCT target_name FROM solutions WHERE initial_board = ?',
            (board_state,)
        )
        available_targets = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Check if board exists but has no solution for this target
        if rows and all(row['moves'] == -1 for row in rows):
            return jsonify({
                'results': [],
                'total_found': 0,
                'search_board': board_state,
                'target': target,
                'available_targets': available_targets,
                'message': f'Board configuration found but has no solution for {target} target',
                'unsolvable': True
            })
        
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
            'available_targets': available_targets,
            'message': f'Found {len(results)} solvable configuration(s) for {target} target' if results else f'No solvable configurations found for {target} target'
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/compare_targets/<int:config_id>')
def compare_targets(config_id):
    """Compare solutions for the same configuration across different targets"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT target_name, target_positions, moves, time_ms 
               FROM solutions WHERE id = ? ORDER BY target_name''',
            (config_id,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({'error': f'Configuration {config_id} not found'}), 404
        
        comparisons = []
        for row in rows:
            comparisons.append({
                'target_name': row['target_name'],
                'target_positions': [int(x) for x in row['target_positions'].split(',')],
                'moves': row['moves'],
                'time_ms': row['time_ms']
            })
        
        return jsonify({
            'config_id': config_id,
            'comparisons': comparisons,
            'total_targets': len(comparisons)
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎯 Enhanced Hippodrome Solution Explorer - Multi-Target API")
    print("=" * 65)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Enhanced database not found: {DB_PATH}")
        print("🔧 Please run 'python create_database_enhanced.py' first.")
        exit(1)
    
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM solutions')
        total_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM targets')
        target_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT name, total_solutions FROM targets ORDER BY total_solutions DESC')
        targets = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Enhanced database connected successfully!")
        print(f"📊 Loaded {total_count:,} solutions across {target_count} targets")
        for target in targets:
            print(f"   • {target[0]}: {target[1]:,} solutions")
        print(f"🚀 Starting enhanced server at http://localhost:5000")
        print(f"💾 Database size: {os.path.getsize(DB_PATH) / (1024*1024):.1f} MB")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Failed to connect to enhanced database: {e}")
        print("🔧 Please run 'python create_database_enhanced.py' first.")
        exit(1) 