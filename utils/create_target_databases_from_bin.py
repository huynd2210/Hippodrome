#!/usr/bin/env python3
"""
Create SQLite databases for each target by decoding compact binary files in encoded_solutions/.
Schema matches the existing frontend expectations so no app changes are needed.
"""
import os
import sqlite3
import struct
from typing import List, Tuple

# Try to import helpers from root; fall back to local implementations
try:
    from transform_solutions import unpack_moves_from_bytes, apply_move
except Exception:
    def unpack_moves_from_bytes(data: bytes) -> List[Tuple[int, int]]:
        """Unpacks a byte string into a list of (from, to) moves."""
        result: List[Tuple[int, int]] = []
        for b in data:
            result.append(((b >> 4) & 0x0F, b & 0x0F))
        return result

    def apply_move(board: str, move: Tuple[int, int]) -> str:
        """Applies a move to a board string and returns the new board string."""
        from_pos, to_pos = move
        if not (0 <= from_pos < 16 and 0 <= to_pos < 16):
            return board
        board_list = list(board)
        board_list[to_pos] = board_list[from_pos]
        board_list[from_pos] = 'x'
        return ''.join(board_list)

# Magic constant for binary file validation
MAGIC = b'HIPP'

# Directory containing the binary solution files
BIN_DIR = os.path.join('encoded_solutions')

# Mapping from binary file name keywords to target names
TARGET_MAP = {
    'og': 'top-row',
    'first_column': 'first-column',
    'last_column': 'last-column',
    'corners': 'corners',
    'center': 'center',
    'bottom': 'bottom-row',
}

# Predefined target positions for each target name
TARGET_POSITIONS = {
    'top-row': [0, 1, 2, 3],
    'bottom-row': [12, 13, 14, 15],
    'first-column': [0, 4, 8, 12],
    'last-column': [3, 7, 11, 15],
    'corners': [0, 3, 12, 15],
    'center': [5, 6, 9, 10],
}


def parse_bin_path_to_target(bin_path: str) -> str:
    """Parses the target name from a binary file path."""
    name = os.path.basename(bin_path).lower()
    for key, target in TARGET_MAP.items():
        if key in name:
            return target
    # Default
    return 'top-row'


def read_bin(bin_path: str):
    """Reads a binary solution file and yields records."""
    with open(bin_path, 'rb') as f:
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError(f'Invalid magic in {bin_path}')
        version = struct.unpack('<B', f.read(1))[0]
        count = struct.unpack('<I', f.read(4))[0]
        for _ in range(count):
            sid = struct.unpack('<I', f.read(4))[0]
            bitboards = [struct.unpack('<H', f.read(2))[0] for _ in range(8)]
            mcount = struct.unpack('<H', f.read(2))[0]
            moves = f.read(mcount)
            yield sid, bitboards, moves


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
            # Should not happen
            chars.append('x')
    return ''.join(chars)


def reconstruct_states(initial_board: str, moves_bytes: bytes) -> List[str]:
    """Reconstructs the full solution path from an initial board and a series of moves."""
    moves: List[Tuple[int, int]] = unpack_moves_from_bytes(moves_bytes)
    states = [initial_board]
    current = initial_board
    for mv in moves:
        current = apply_move(current, mv)
        states.append(current)
    return states


def create_db_for_target(bin_path: str, target_name: str) -> str:
    """Creates a SQLite database for a given target from a binary solution file."""
    db_path = f"hippodrome_{target_name.replace('-', '_')}.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Schema
    cur.execute('''
        CREATE TABLE solutions (
            id INTEGER PRIMARY KEY,
            initial_board TEXT NOT NULL,
            solution_path TEXT NOT NULL,
            moves INTEGER NOT NULL,
            time_ms REAL NOT NULL
        )
    ''')
    cur.execute('CREATE INDEX idx_moves ON solutions(moves)')
    cur.execute('CREATE INDEX idx_time ON solutions(time_ms)')
    cur.execute('CREATE INDEX idx_board ON solutions(initial_board)')

    cur.execute('''
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    cur.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('target_name', target_name))
    cur.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('target_positions', ','.join(map(str, TARGET_POSITIONS.get(target_name, [])))))
    cur.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('target_description', target_name))

    # Insert records
    batch = []
    batch_size = 10000
    total = 0
    for sid, bitboards, moves_bytes in read_bin(bin_path):
        initial = board_from_bitboards(bitboards)
        states = reconstruct_states(initial, moves_bytes)
        moves_cnt = max(0, len(states) - 1)
        solution_path = ';'.join(states)
        # time_ms unknown in binary → 0.0
        batch.append((sid, initial, solution_path, moves_cnt, 0.0))
        total += 1
        if len(batch) >= batch_size:
            cur.executemany('INSERT INTO solutions (id, initial_board, solution_path, moves, time_ms) VALUES (?, ?, ?, ?, ?)', batch)
            conn.commit()
            batch.clear()
            if total % 50000 == 0:
                print(f"  Inserted {total:,} into {db_path}...")
    if batch:
        cur.executemany('INSERT INTO solutions (id, initial_board, solution_path, moves, time_ms) VALUES (?, ?, ?, ?, ?)', batch)
    cur.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('total_solutions', str(total)))
    conn.commit()
    conn.close()
    print(f"Created {db_path} ({total:,} records)")
    return db_path


def create_targets_index(db_files: List[str]):
    """Creates a main index database that points to the individual target databases."""
    index_path = 'targets_index.db'
    if os.path.exists(index_path):
        os.remove(index_path)
    conn = sqlite3.connect(index_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE targets (
            name TEXT PRIMARY KEY,
            positions TEXT NOT NULL,
            description TEXT NOT NULL,
            database_file TEXT NOT NULL,
            total_solutions INTEGER NOT NULL
        )
    ''')
    for db_file in db_files:
        tconn = sqlite3.connect(db_file)
        tcur = tconn.cursor()
        tcur.execute('SELECT value FROM metadata WHERE key = "target_name"')
        name = tcur.fetchone()[0]
        tcur.execute('SELECT value FROM metadata WHERE key = "target_positions"')
        positions = tcur.fetchone()[0]
        tcur.execute('SELECT value FROM metadata WHERE key = "total_solutions"')
        total = int(tcur.fetchone()[0])
        cur.execute('INSERT INTO targets (name, positions, description, database_file, total_solutions) VALUES (?, ?, ?, ?, ?)',
                    (name, positions, name, db_file, total))
        tconn.close()
    conn.commit()
    conn.close()
    print(f"Created targets index: {index_path}")


def main():
    """Main function to find binary files and create databases."""
    if not os.path.isdir(BIN_DIR):
        print(f"Directory not found: {BIN_DIR}")
        return 1
    bin_files = [os.path.join(BIN_DIR, f) for f in os.listdir(BIN_DIR) if f.endswith('.bin')]
    if not bin_files:
        print(f"No .bin files found in {BIN_DIR}")
        return 1
    print(f"Found {len(bin_files)} binary files:")
    for bf in bin_files:
        print(f"  • {os.path.basename(bf)} -> {parse_bin_path_to_target(bf)}")

    # Skip sample_* bins and avoid duplicate processing per target
    processed_targets = set()
    created = []
    for bf in bin_files:
        base = os.path.basename(bf).lower()
        if base.startswith('sample_'):
            print(f"Skipping sample binary: {base}")
            continue
        target = parse_bin_path_to_target(bf)
        if target in processed_targets:
            print(f"Skipping duplicate target '{target}' from {base}")
            continue
        db = create_db_for_target(bf, target)
        created.append(db)
        processed_targets.add(target)

    create_targets_index(created)
    print("Databases ready from binary inputs")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())