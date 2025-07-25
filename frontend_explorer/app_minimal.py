from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve minimal page with no initial data loading"""
    return render_template('minimal.html')

@app.route('/api/quick-targets')
def get_quick_targets():
    """Get targets list quickly - only called when user clicks"""
    try:
        # Return hardcoded targets first for instant response
        return jsonify({
            'targets': [
                {'name': 'first-column', 'positions': [0,4,8,12], 'description': 'Knights to first column'},
                {'name': 'last-column', 'positions': [3,7,11,15], 'description': 'Knights to last column'},
                {'name': 'top-row', 'positions': [0,1,2,3], 'description': 'Knights to top row'}
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-random')
def get_quick_random():
    """Get one random solution quickly"""
    target = request.args.get('target', 'first-column')
    
    try:
        # Simple hardcoded example for instant response
        if target == 'first-column':
            return jsonify({
                'id': 12345,
                'target_name': 'first-column',
                'target_positions': [0,4,8,12],
                'initial_board': 'KBRKBRRKKRBxNNNN',
                'solution_path': ['KBRKBRRKKRBxNNNN', 'KBRKBRRKKRBNNxNN', 'KBRKBRRKxRBNNKNN'],
                'moves': 2,
                'time_ms': 15.5,
                'total_steps': 3
            })
        else:
            return jsonify({
                'id': 54321,
                'target_name': target,
                'target_positions': [3,7,11,15],
                'initial_board': 'RRxBRKBBKBRKNNNN',
                'solution_path': ['RRxBRKBBKBRKNNNN', 'RRNBRKBBKBRKNxNN'],
                'moves': 1,
                'time_ms': 8.2,
                'total_steps': 2
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'minimal_ready', 'message': 'Instant loading!'})

if __name__ == '__main__':
    print("🎯 Minimal Hippodrome Explorer - Instant Loading")
    print("=" * 50)
    print("✅ No database loading - instant startup!")
    print("🚀 Starting at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 