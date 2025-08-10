#!/usr/bin/env python3
"""
This script runs a Flask web application for exploring Hippodrome puzzle solutions.
It provides a frontend interface and a set of API endpoints to query solution data.

The application can be configured to use two different backend data sources:
1.  'bin': Reads data directly from compact binary files. This is the default.
2.  'db': Connects to SQLite databases for solution data.

The backend can be selected by setting the HIPPO_SOURCE environment variable.
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sqlite3
import random
import struct
import urllib.request
import tempfile
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Determine the backend data source from environment variables (default to 'bin')
HIPPO_SOURCE = os.environ.get('HIPPO_SOURCE', 'bin').lower()

# --- Configuration and Constants ---

# Directories
ROOT_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = (ROOT_DIR / 'encoded_solutions').resolve()

# Binary metadata
MAGIC = b'HIPP'
TARGETS = ['top-row', 'first-column', 'last-column', 'corners', 'center']
TARGET_POSITIONS = {
    'top-row': [0, 1, 2, 3],
    'bottom-row': [12, 13, 14, 15],
    'first-column': [0, 4, 8, 12],
    'last-column': [3, 7, 11, 15],
    'corners': [0, 3, 12, 15],
    'center': [5, 6, 9, 10],
}
TARGET_BIN_MAP = {
    'top-row': 'hippodrome_solutions_og.bin',
    'first-column': 'hippodrome_solutions_first_column.bin',
    'last-column': 'hippodrome_solutions_last_column.bin',
    'corners': 'hippodrome_solutions_corners.bin',
    'center': 'hippodrome_solutions_center.bin',
}
TARGET_DB_MAP = {
    'top-row': 'hippodrome_top_row.db',
        'first-column': 'hippodrome_first_column.db',
        'last-column': 'hippodrome_last_column.db',
        'corners': 'hippodrome_corners.db',
    'center': 'hippodrome_center.db',
}

# Optional remote URLs for cloud deployments
BIN_URLS = {
    'top-row': os.environ.get('BIN_URL_TOP_ROW', ''),
    'first-column': os.environ.get('BIN_URL_FIRST_COLUMN', ''),
    'last-column': os.environ.get('BIN_URL_LAST_COLUMN', ''),
    'corners': os.environ.get('BIN_URL_CORNERS', ''),
    'center': os.environ.get('BIN_URL_CENTER', ''),
}
DB_URLS = {
    'targets_index': os.environ.get('DB_URL_TARGETS_INDEX', ''),
    'top-row': os.environ.get('DB_URL_TOP_ROW', ''),
    'first-column': os.environ.get('DB_URL_FIRST_COLUMN', ''),
    'last-column': os.environ.get('DB_URL_LAST_COLUMN', ''),
    'corners': os.environ.get('DB_URL_CORNERS', ''),
    'center': os.environ.get('DB_URL_CENTER', ''),
}

# Caching for downloaded files
CACHE_DIR = Path(tempfile.gettempdir()) / 'hippodrome_cache'
CACHE_DIR.mkdir(exist_ok=True)


def download_to_cache(url: str, key_hint: str) -> Optional[str]:
    """Downloads a file from a URL to a local cache directory."""
    if not url:
        return None
    h = hashlib.md5(url.encode()).hexdigest()
    path = CACHE_DIR / f"{key_hint}_{h}"
    if path.exists():
        return str(path)
    try:
        urllib.request.urlretrieve(url, path)
        return str(path)
    except Exception:
        return None


# --------------- BIN BACKEND ---------------

def board_from_bitboards(bitboards: List[int]) -> str:
    """Reconstructs a board string from a list of bitboards."""
    k1, k2, k3, k4, rooks, bishops, kings, empty = bitboards
    chars = []
    for i in range(16):
        mask = 1 << i
        if (k1 | k2 | k3 | k4) & mask:
            chars.append('N')
        elif rooks & mask:
            chars.append('R')
        elif bishops & mask:
            chars.append('B')
        elif kings & mask:
            chars.append('K')
        elif empty & mask:
            chars.append('x')
        else:
            chars.append('x')
    return ''.join(chars)

def unpack_moves_from_bytes(data: bytes) -> List[Tuple[int, int]]:
    """Unpacks a byte string into a list of (from, to) moves."""
    return [(((b >> 4) & 0x0F), (b & 0x0F)) for b in data]

def apply_move(board: str, move: Tuple[int, int]) -> str:
    """Applies a move to a board string and returns the new board string."""
    from_pos, to_pos = move
    bl = list(board)
    bl[to_pos] = bl[from_pos]
    bl[from_pos] = 'x'
    return ''.join(bl)

def reconstruct_states(initial_board: str, moves_bytes: bytes) -> List[str]:
    """Reconstructs the full solution path from an initial board and a series of moves."""
    states = [initial_board]
    current = initial_board
    for mv in unpack_moves_from_bytes(moves_bytes):
        try:
            from_pos, to_pos = mv
            # Defensive bounds check to avoid IndexError on corrupted data
            if not (0 <= from_pos < 16 and 0 <= to_pos < 16):
                continue
            current = apply_move(current, (from_pos, to_pos))
            states.append(current)
        except IndexError:
            # Stop reconstruction on invalid move to avoid server error
            break
    return states

class BinTargetIndex:
    """An in-memory index for a single binary solution file."""
    def __init__(self, target_name: str):
        self.target = target_name
        self.path = self._resolve_path()
        self.file = None  # type: Optional[object]
        self.version = 0
        self.count = 0
        self.entries: List[Dict] = []
        self.id_to_idx: Dict[int, int] = {}
        self.min_moves = None
        self.max_moves = None
        self.sum_moves = 0
        self._lock = threading.Lock()

    def _resolve_path(self) -> str:
        """Resolves the path to the binary file, downloading it if necessary."""
        filename = TARGET_BIN_MAP[self.target]
        local_path = BIN_DIR / filename
        if local_path.exists():
            return str(local_path)
        # Try remote URL
        url = BIN_URLS.get(self.target, '')
        cached = download_to_cache(url, f"{self.target}.bin") if url else None
        if cached:
            return cached
        raise FileNotFoundError(f"Binary not found for target {self.target}")

    def open(self):
        """Opens the binary file and builds the in-memory index."""
        if self.file is None:
            with self._lock:
                if self.file is None:
                    self.file = open(self.path, 'rb')
                    self._build_index()
                    # After building index from scan, persist sidecar for faster startups
                    try:
                        self._persist_index()
                    except Exception:
                        pass

    def _build_index(self):
        """Reads a sidecar index if present; otherwise scans the binary to build one."""
        idx_path = self.path + '.idx'
        if os.path.exists(idx_path):
            with open(idx_path, 'rb') as idx:
                sig = idx.read(4)
                if sig != b'HIPX':
                    raise ValueError('Invalid index signature')
                ver = struct.unpack('<B', idx.read(1))[0]
                cnt = struct.unpack('<I', idx.read(4))[0]
                self.version = ver
                self.count = cnt
                for i in range(cnt):
                    sid = struct.unpack('<I', idx.read(4))[0]
                    offset = struct.unpack('<Q', idx.read(8))[0]
                    mcount = struct.unpack('<H', idx.read(2))[0]
                    initial_bytes = idx.read(16)
                    initial = initial_bytes.decode('ascii')
                    self.entries.append({'id': sid, 'offset': offset, 'initial_board': initial, 'moves_count': mcount})
                    self.id_to_idx[sid] = i
                    self.min_moves = mcount if self.min_moves is None else min(self.min_moves, mcount)
                    self.max_moves = mcount if self.max_moves is None else max(self.max_moves, mcount)
                    self.sum_moves += mcount
            return
        # Fallback: scan the binary file
        f = self.file
        f.seek(0)
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError(f'Invalid magic in {self.path}')
        self.version = struct.unpack('<B', f.read(1))[0]
        self.count = struct.unpack('<I', f.read(4))[0]
        for i in range(self.count):
            offset = f.tell()
            sid = struct.unpack('<I', f.read(4))[0]
            bitboards = [struct.unpack('<H', f.read(2))[0] for _ in range(8)]
            initial = board_from_bitboards(bitboards)
            mcount = struct.unpack('<H', f.read(2))[0]
            f.seek(mcount, os.SEEK_CUR)
            self.min_moves = mcount if self.min_moves is None else min(self.min_moves, mcount)
            self.max_moves = mcount if self.max_moves is None else max(self.max_moves, mcount)
            self.sum_moves += mcount
            self.id_to_idx[sid] = i
            self.entries.append({'id': sid, 'offset': offset, 'initial_board': initial, 'moves_count': mcount})

    def _read_entry(self, idx: int):
        """Reads a single solution entry from the binary file by its index."""
        f = self.file
        # Defensive: guard against race on idx during initial warmup
        if idx < 0 or idx >= len(self.entries):
            raise IndexError('entry index out of range')
        meta = self.entries[idx]
        f.seek(meta['offset'])
        sid = struct.unpack('<I', f.read(4))[0]
        bitboards = [struct.unpack('<H', f.read(2))[0] for _ in range(8)]
        mcount = struct.unpack('<H', f.read(2))[0]
        moves = f.read(mcount)
        return sid, bitboards, moves

    def get_by_id(self, sid: int):
        """Retrieves a solution by its configuration ID."""
        self.open()
        idx = self.id_to_idx.get(sid)
        if idx is None:
            return None
        try:
            return self._read_entry(idx)
        except IndexError:
            return None

    def get_random(self):
        """Retrieves a random solution."""
        self.open()
        if self.count <= 0:
            raise IndexError('no entries in index')
        try:
            return self._read_entry(random.randrange(self.count))
        except IndexError:
            # Retry once on transient out-of-range
            return self._read_entry(0)

    def get_stats(self):
        """Returns statistics about the solutions in the binary file."""
        self.open()
        avg_moves = (self.sum_moves / self.count) if self.count else 0.0
        return {'total_solutions': self.count, 'avg_moves': round(avg_moves, 2), 'min_moves': self.min_moves or 0, 'max_moves': self.max_moves or 0}

    def find_by_board(self, board_state: str):
        """Finds a solution by its initial board state."""
        self.open()
        for i, meta in enumerate(self.entries):
            if meta['initial_board'] == board_state:
                return self._read_entry(i)
        return None

    def _persist_index(self):
        """Writes a compact sidecar index (.idx) next to the binary for fast reloads."""
        idx_path = self.path + '.idx'
        # Do not overwrite if already present
        if os.path.exists(idx_path):
            return
        with open(idx_path, 'wb') as idx:
            idx.write(b'HIPX')               # signature
            idx.write(struct.pack('<B', self.version))
            idx.write(struct.pack('<I', self.count))
            for meta in self.entries:
                idx.write(struct.pack('<I', meta['id']))
                idx.write(struct.pack('<Q', meta['offset']))
                idx.write(struct.pack('<H', meta['moves_count']))
                # Store initial board as 16 bytes ASCII
                initial = meta['initial_board'].encode('ascii')[:16]
                if len(initial) < 16:
                    initial += b' ' * (16 - len(initial))
                idx.write(initial)

_BIN_INDICES: Dict[str, BinTargetIndex] = {}

def get_bin_index(target: str) -> BinTargetIndex:
    """Returns a cached instance of a BinTargetIndex for a given target."""
    if target not in _BIN_INDICES:
        _BIN_INDICES[target] = BinTargetIndex(target)
    return _BIN_INDICES[target]


# --------------- DB BACKEND ---------------

def get_target_db_connection(target_name: str):
    """Returns a connection to the SQLite database for a given target."""
    db_file = TARGET_DB_MAP.get(target_name, f"hippodrome_{target_name.replace('-', '_')}.db")
    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn
    # remote
    url = DB_URLS.get(target_name, '')
    if not url:
        raise FileNotFoundError(f"Target database not found: {db_file}")
    cache_path = download_to_cache(url, f"{target_name}.db")
    if not cache_path:
        raise FileNotFoundError(f"Failed to download database for {target_name}")
    conn = sqlite3.connect(cache_path)
    conn.row_factory = sqlite3.Row
    return conn


def parse_solution_path(solution_path_str: str) -> List[str]:
    """Parses a semicolon-separated solution path string into a list of board states."""
    if not solution_path_str:
        return []
    return [s for s in solution_path_str.split(';')]


# --------------- ROUTES ---------------

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/targets')
def get_targets():
    """Returns a list of available targets."""
    targets = []
    for t in TARGETS:
        if HIPPO_SOURCE == 'bin':
            fname = TARGET_BIN_MAP[t]
            local = (BIN_DIR / fname).exists()
            remote = bool(BIN_URLS.get(t, ''))
            if not (local or remote):
                continue
        else:
            local = os.path.exists(TARGET_DB_MAP[t])
            remote = bool(DB_URLS.get(t, ''))
            if not (local or remote):
                continue
        targets.append({'name': t, 'positions': ','.join(map(str, TARGET_POSITIONS.get(t, []))), 'description': t})
    return jsonify(targets)

@app.route('/api/solution/<int:config_id>')
def get_solution(config_id):
    """Returns a specific solution by its configuration ID."""
    target = request.args.get('target', 'top-row')
    try:
        if HIPPO_SOURCE == 'bin':
            idx = get_bin_index(target)
            data = idx.get_by_id(config_id)
            if not data:
                return jsonify({'error': f'Solution not found for config {config_id} with target {target}'}), 404
            sid, bitboards, moves_bytes = data
            initial_board = board_from_bitboards(bitboards)
            states = reconstruct_states(initial_board, moves_bytes)
            if not states or states[0] != initial_board:
                return jsonify({'error': 'Corrupted solution data'}), 500
            return jsonify({'id': sid, 'initial_board': initial_board, 'solution_path': states, 'moves': len(states) - 1, 'time_ms': 0.0, 'target': target})
        else:
            conn = get_target_db_connection(target)
            cur = conn.cursor()
            cur.execute('SELECT id, initial_board, solution_path, moves, time_ms FROM solutions WHERE id = ?', (config_id,))
            row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({'error': f'Solution not found for config {config_id} with target {target}'}), 404
            return jsonify({'id': row['id'], 'initial_board': row['initial_board'], 'solution_path': parse_solution_path(row['solution_path']), 'moves': row['moves'], 'time_ms': row['time_ms'], 'target': target})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/random')
def get_random_solution():
    """Returns a random solution."""
    target = request.args.get('target', 'top-row') 
    try:
        if HIPPO_SOURCE == 'bin':
            idx = get_bin_index(target)
            sid, bitboards, moves_bytes = idx.get_random()
            initial_board = board_from_bitboards(bitboards)
            states = reconstruct_states(initial_board, moves_bytes)
            if not states or states[0] != initial_board:
                return jsonify({'error': 'Corrupted solution data'}), 500
            return jsonify({'id': sid, 'initial_board': initial_board, 'solution_path': states, 'moves': len(states) - 1, 'time_ms': 0.0, 'target': target})
        else:
            conn = get_target_db_connection(target)
            cur = conn.cursor()
            cur.execute('SELECT id, initial_board, solution_path, moves, time_ms FROM solutions ORDER BY RANDOM() LIMIT 1')
            row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({'error': f'No solutions found for target {target}'}), 404
            return jsonify({'id': row['id'], 'initial_board': row['initial_board'], 'solution_path': parse_solution_path(row['solution_path']), 'moves': row['moves'], 'time_ms': row['time_ms'], 'target': target})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_solutions():
    """Searches for solutions based on a range of moves."""
    target = request.args.get('target', 'top-row')
    min_moves = request.args.get('min_moves', type=int)
    max_moves = request.args.get('max_moves', type=int)
    limit = min(request.args.get('limit', 10, type=int), 100)
    try:
        if HIPPO_SOURCE == 'bin':
            idx = get_bin_index(target)
            results = []
            for meta in idx.entries:
                m = meta['moves_count']
                if min_moves is not None and m < min_moves:
                    continue
                if max_moves is not None and m > max_moves:
                    continue
                results.append({'id': meta['id'], 'initial_board': meta['initial_board'], 'moves': m, 'time_ms': 0.0})
                if len(results) >= limit:
                    break
            return jsonify(results)
        else:
            conn = get_target_db_connection(target)
            cur = conn.cursor()
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
        cur.execute(query, params)
        results = [dict(row) for row in cur.fetchall()]
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_statistics():
    """Returns statistics about the solutions for a given target."""
    target = request.args.get('target', 'top-row')
    try:
        if HIPPO_SOURCE == 'bin':
            idx = get_bin_index(target)
            s = idx.get_stats()
            return jsonify({'target': target, 'total_solutions': s['total_solutions'], 'avg_moves': s['avg_moves'], 'min_moves': s['min_moves'], 'max_moves': s['max_moves'], 'avg_time_ms': 0.0, 'move_distribution': []})
        else:
            conn = get_target_db_connection(target)
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) as total FROM solutions')
            total = cur.fetchone()[0]
            cur.execute('SELECT AVG(moves), MIN(moves), MAX(moves) FROM solutions')
            avg_moves, min_moves, max_moves = cur.fetchone()
            cur.execute('SELECT AVG(time_ms) FROM solutions')
            avg_time = cur.fetchone()[0]
            conn.close()
            return jsonify({'target': target, 'total_solutions': total, 'avg_moves': round(avg_moves, 2), 'min_moves': min_moves, 'max_moves': max_moves, 'avg_time_ms': round(avg_time, 2), 'move_distribution': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_by_board')
def search_by_board():
    """Searches for a solution by its initial board state."""
    board_state = request.args.get('board', '')
    target = request.args.get('target', 'top-row')
    if len(board_state) != 16:
        return jsonify({'error': 'Board state must be exactly 16 characters'}), 400
    try:
        if HIPPO_SOURCE == 'bin':
            idx = get_bin_index(target)
            data = idx.find_by_board(board_state)
            if not data:
                return jsonify({'error': f'No solution found for this board configuration with target {target}'}), 404
            sid, bitboards, moves_bytes = data
            initial_board = board_from_bitboards(bitboards)
            states = reconstruct_states(initial_board, moves_bytes)
            if not states or states[0] != initial_board:
                return jsonify({'error': 'Corrupted solution data'}), 500
            return jsonify({'id': sid, 'initial_board': initial_board, 'solution_path': states, 'moves': len(states) - 1, 'time_ms': 0.0, 'target': target})
        else:
            conn = get_target_db_connection(target)
            cur = conn.cursor()
            cur.execute('SELECT id, initial_board, solution_path, moves, time_ms FROM solutions WHERE initial_board = ?', (board_state,))
            row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({'error': f'No solution found for this board configuration with target {target}'}), 404
            return jsonify({'id': row['id'], 'initial_board': row['initial_board'], 'solution_path': parse_solution_path(row['solution_path']), 'moves': row['moves'], 'time_ms': row['time_ms'], 'target': target})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """A health check endpoint to verify that the application is running and has data."""
    if HIPPO_SOURCE == 'bin':
        available = any((BIN_DIR / TARGET_BIN_MAP[t]).exists() or BIN_URLS.get(t, '') for t in TARGETS)
        return jsonify({'status': 'ready' if available else 'missing-binaries'})
    else:
        available = any(os.path.exists(TARGET_DB_MAP[t]) or DB_URLS.get(t, '') for t in TARGETS)
        return jsonify({'status': 'ready' if available else 'missing-databases'})


if __name__ == '__main__':
    print(f"🎯 Hippodrome Explorer (Unified, source={HIPPO_SOURCE}) starting...")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)