from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import random
import json
from functools import lru_cache

app = Flask(__name__)
CORS(app)

# Database path
DB_PATH = "hippodrome_solutions.db"

def get_db_connection():
    """Get a database connection with row factory for dict-like access"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    
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
    return render_template('index.html')

@app.route('/api/solution/<int:config_id>')
def get_solution(config_id):
    """Get a specific solution by configuration ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, initial_board, solution_path, moves, time_ms FROM solutions WHERE id = ?',
            (config_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': f'Solution not found for ID {config_id}'}), 404
        
        solution_path = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
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
    """Get a random solution from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get a random solution using RANDOM()
        cursor.execute(
            'SELECT id, initial_board, solution_path, moves, time_ms FROM solutions ORDER BY RANDOM() LIMIT 1'
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'No solutions found'}), 404
        
        solution_path = parse_solution_path(row['solution_path'])
        
        return jsonify({
            'id': row['id'],
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
    """Search solutions with filters"""
    try:
        # Get query parameters
        min_moves = request.args.get('min_moves', type=int)
        max_moves = request.args.get('max_moves', type=int)
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db_connection()
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
            'showing': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/stats')
def get_statistics():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute('SELECT COUNT(*) FROM solutions')
        total_solutions = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(moves), MAX(moves), AVG(moves) FROM solutions')
        min_moves, max_moves, avg_moves = cursor.fetchone()
        
        cursor.execute('SELECT AVG(moves) FROM (SELECT moves FROM solutions ORDER BY moves LIMIT 2 - (SELECT COUNT(*) FROM solutions) % 2 OFFSET (SELECT (COUNT(*) - 1) / 2 FROM solutions))')
        median_moves = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(time_ms), MAX(time_ms), AVG(time_ms) FROM solutions')
        min_time, max_time, avg_time = cursor.fetchone()
        
        # Get move distribution
        cursor.execute('SELECT moves, COUNT(*) FROM solutions GROUP BY moves ORDER BY moves')
        move_distribution = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        stats = {
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
    """Get the most interesting solutions (hardest, fastest, etc.)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get extreme cases
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions ORDER BY moves DESC LIMIT 1')
        hardest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions ORDER BY moves ASC LIMIT 1')
        easiest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions ORDER BY time_ms ASC LIMIT 1')
        fastest = cursor.fetchone()
        
        cursor.execute('SELECT id, initial_board, moves, time_ms FROM solutions ORDER BY time_ms DESC LIMIT 1')
        slowest = cursor.fetchone()
        
        conn.close()
        
        def format_solution(row):
            return {
                'id': row['id'],
                'initial_board': row['initial_board'],
                'moves': row['moves'],
                'time_ms': row['time_ms']
            }
        
        return jsonify({
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
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'total_solutions': count
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/search_by_board', methods=['POST'])
def search_by_board():
    """Search for solutions by board configuration"""
    try:
        data = request.get_json()
        board_state = data.get('board_state')
        
        if not board_state:
            return jsonify({'error': 'board_state is required'}), 400
            
        if len(board_state) != 16:
            return jsonify({'error': 'board_state must be exactly 16 characters'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search for exact matches
        cursor.execute(
            'SELECT id, initial_board, moves FROM solutions WHERE initial_board = ? LIMIT 10', 
            (board_state,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        # Check if board exists but has no solution
        if rows and all(row['moves'] == -1 for row in rows):
            return jsonify({
                'results': [],
                'total_found': 0,
                'search_board': board_state,
                'message': 'Board configuration found but has no solution',
                'unsolvable': True
            })
        
        # Filter out unsolvable configurations (moves = -1)
        results = []
        for row in rows:
            if row['moves'] != -1:  # Only include solvable configurations
                results.append({
                    'id': row['id'],
                    'initial_board': row['initial_board'],
                    'moves': row['moves']
                })
        
        return jsonify({
            'results': results,
            'total_found': len(results),
            'search_board': board_state,
            'message': f'Found {len(results)} solvable configuration(s)' if results else 'No solvable configurations found'
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎯 Hippodrome Solution Explorer - SQLite Backend API")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print("🔧 Please run 'python create_database.py' first to create the database.")
        exit(1)
    
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM solutions')
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Database connected successfully!")
        print(f"📊 Loaded {count:,} solutions from SQLite database")
        print(f"🚀 Starting server at http://localhost:5000")
        print(f"💾 Database size: {os.path.getsize(DB_PATH) / (1024*1024):.1f} MB")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("🔧 Please run 'python create_database.py' first to create the database.")
        exit(1) 