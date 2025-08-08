from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import random
import struct
from typing import Dict, List, Tuple, Optional

app = Flask(__name__)
CORS(app)

BIN_DIR = os.path.join(os.path.dirname(__file__), '..', 'encoded_solutions')
BIN_DIR = os.path.abspath(BIN_DIR)

MAGIC = b'HIPP'

TARGET_BIN_MAP = {
    'top-row': 'hippodrome_solutions_og.bin',
    'first-column': 'hippodrome_solutions_first_column.bin',
    'last-column': 'hippodrome_solutions_last_column.bin',
    'corners': 'hippodrome_solutions_corners.bin',
    'center': 'hippodrome_solutions_center.bin',
}

TARGET_POSITIONS = {
    'top-row': [0, 1, 2, 3],
    'bottom-row': [12, 13, 14, 15],
    'first-column': [0, 4, 8, 12],
    'last-column': [3, 7, 11, 15],
    'corners': [0, 3, 12, 15],
    'center': [5, 6, 9, 10],
}


def board_from_bitboards(bitboards: List[int]) -> str:
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
    return [(((b >> 4) & 0x0F), (b & 0x0F)) for b in data]


def apply_move(board: str, move: Tuple[int, int]) -> str:
    from_pos, to_pos = move
    bl = list(board)
    bl[to_pos] = bl[from_pos]
    bl[from_pos] = 'x'
    return ''.join(bl)


def reconstruct_states(initial_board: str, moves_bytes: bytes) -> List[str]:
    states = [initial_board]
    current = initial_board
    for mv in unpack_moves_from_bytes(moves_bytes):
        current = apply_move(current, mv)
        states.append(current)
    return states


class BinTargetIndex:
    def __init__(self, target_name: str, bin_path: str):
        self.target = target_name
        self.bin_path = bin_path
        self.file = None  # type: Optional[object]
        self.version = 0
        self.count = 0
        # index of entries: list of dicts with keys: id, offset, initial_board, moves_count
        self.entries: List[Dict] = []
        self.id_to_idx: Dict[int, int] = {}
        # stats
        self.min_moves = None
        self.max_moves = None
        self.sum_moves = 0

    def open(self):
        if self.file is None:
            self.file = open(self.bin_path, 'rb')
            self._build_index()

    def _build_index(self):
        f = self.file
        f.seek(0)
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError(f'Invalid magic in {self.bin_path}')
        self.version = struct.unpack('<B', f.read(1))[0]
        self.count = struct.unpack('<I', f.read(4))[0]
        # Walk records
        for i in range(self.count):
            offset = f.tell()
            sid = struct.unpack('<I', f.read(4))[0]
            bitboards = [struct.unpack('<H', f.read(2))[0] for _ in range(8)]
            initial = board_from_bitboards(bitboards)
            mcount = struct.unpack('<H', f.read(2))[0]
            # Skip moves bytes to next record
            f.seek(mcount, os.SEEK_CUR)
            # Record stats
            self.min_moves = mcount if self.min_moves is None else min(self.min_moves, mcount)
            self.max_moves = mcount if self.max_moves is None else max(self.max_moves, mcount)
            self.sum_moves += mcount
            self.id_to_idx[sid] = i
            self.entries.append({
                'id': sid,
                'offset': offset,
                'initial_board': initial,
                'moves_count': mcount,
            })

    def _read_entry(self, idx: int):
        f = self.file
        entry_meta = self.entries[idx]
        f.seek(entry_meta['offset'])
        sid = struct.unpack('<I', f.read(4))[0]
        bitboards = [struct.unpack('<H', f.read(2))[0] for _ in range(8)]
        mcount = struct.unpack('<H', f.read(2))[0]
        moves = f.read(mcount)
        return sid, bitboards, moves

    def get_by_id(self, sid: int):
        self.open()
        idx = self.id_to_idx.get(sid)
        if idx is None:
            return None
        return self._read_entry(idx)

    def get_random(self):
        self.open()
        idx = random.randrange(self.count)
        return self._read_entry(idx)

    def get_stats(self):
        self.open()
        avg_moves = (self.sum_moves / self.count) if self.count else 0.0
        return {
            'total_solutions': self.count,
            'avg_moves': round(avg_moves, 2),
            'min_moves': self.min_moves or 0,
            'max_moves': self.max_moves or 0,
        }

    def find_by_board(self, board_state: str):
        self.open()
        for idx, meta in enumerate(self.entries):
            if meta['initial_board'] == board_state:
                return self._read_entry(idx)
        return None


# Cache of targets to indices
_BIN_INDICES: Dict[str, BinTargetIndex] = {}


def get_target_index(target_name: str) -> BinTargetIndex:
    if target_name not in TARGET_BIN_MAP:
        raise ValueError(f"Unknown target: {target_name}")
    bin_file = TARGET_BIN_MAP[target_name]
    bin_path = os.path.join(BIN_DIR, bin_file)
    if not os.path.exists(bin_path):
        raise FileNotFoundError(f"Binary not found for target {target_name}: {bin_path}")
    key = target_name
    if key not in _BIN_INDICES:
        _BIN_INDICES[key] = BinTargetIndex(target_name, bin_path)
    return _BIN_INDICES[key]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/targets')
def get_targets():
    # List available targets based on present binaries
    targets = []
    for t, fname in TARGET_BIN_MAP.items():
        if os.path.exists(os.path.join(BIN_DIR, fname)):
            targets.append({
                'name': t,
                'positions': ','.join(map(str, TARGET_POSITIONS.get(t, []))),
                'description': t,
            })
    return jsonify(targets)


@app.route('/api/solution/<int:config_id>')
def get_solution(config_id):
    target = request.args.get('target', 'top-row')
    try:
        idx = get_target_index(target)
        data = idx.get_by_id(config_id)
        if not data:
            return jsonify({'error': f'Solution not found for config {config_id} with target {target}'}), 404
        sid, bitboards, moves_bytes = data
        initial_board = board_from_bitboards(bitboards)
        states = reconstruct_states(initial_board, moves_bytes)
        return jsonify({
            'id': sid,
            'initial_board': initial_board,
            'solution_path': states,
            'moves': len(states) - 1,
            'time_ms': 0.0,
            'target': target
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/random')
def get_random_solution():
    target = request.args.get('target', 'top-row')
    try:
        idx = get_target_index(target)
        sid, bitboards, moves_bytes = idx.get_random()
        initial_board = board_from_bitboards(bitboards)
        states = reconstruct_states(initial_board, moves_bytes)
        return jsonify({
            'id': sid,
            'initial_board': initial_board,
            'solution_path': states,
            'moves': len(states) - 1,
            'time_ms': 0.0,
            'target': target
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search')
def search_solutions():
    target = request.args.get('target', 'top-row')
    min_moves = request.args.get('min_moves', type=int)
    max_moves = request.args.get('max_moves', type=int)
    limit = min(request.args.get('limit', 10, type=int), 100)
    try:
        idx = get_target_index(target)
        results = []
        for meta in idx.entries:
            moves = meta['moves_count']
            if min_moves is not None and moves < min_moves:
                continue
            if max_moves is not None and moves > max_moves:
                continue
            results.append({'id': meta['id'], 'initial_board': meta['initial_board'], 'moves': moves, 'time_ms': 0.0})
            if len(results) >= limit:
                break
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_statistics():
    target = request.args.get('target', 'top-row')
    try:
        idx = get_target_index(target)
        stats = idx.get_stats()
        return jsonify({
            'target': target,
            'total_solutions': stats['total_solutions'],
            'avg_moves': stats['avg_moves'],
            'min_moves': stats['min_moves'],
            'max_moves': stats['max_moves'],
            'avg_time_ms': 0.0,
            'move_distribution': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search_by_board')
def search_by_board():
    board_state = request.args.get('board', '')
    target = request.args.get('target', 'top-row')
    if len(board_state) != 16:
        return jsonify({'error': 'Board state must be exactly 16 characters'}), 400
    try:
        idx = get_target_index(target)
        data = idx.find_by_board(board_state)
        if not data:
            return jsonify({'error': f'No solution found for this board configuration with target {target}'}), 404
        sid, bitboards, moves_bytes = data
        initial_board = board_from_bitboards(bitboards)
        states = reconstruct_states(initial_board, moves_bytes)
        return jsonify({
            'id': sid,
            'initial_board': initial_board,
            'solution_path': states,
            'moves': len(states) - 1,
            'time_ms': 0.0,
            'target': target
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health_check():
    # Verify that at least one binary exists
    available = any(os.path.exists(os.path.join(BIN_DIR, f)) for f in TARGET_BIN_MAP.values())
    return jsonify({'status': 'ready' if available else 'missing-binaries'})


if __name__ == '__main__':
    print('🎯 Hippodrome Explorer (Binary Mode) starting...')
    print(f'📦 Using binaries from: {BIN_DIR}')
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 