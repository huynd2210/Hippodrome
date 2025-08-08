#!/usr/bin/env python3
import csv
import os
import struct
import argparse
from typing import List, Tuple, Optional

from transform_solutions import (
    parse_solution_path_flexible,
    unpack_moves_from_bytes,
    apply_move,
)

MAGIC = b'HIPP'

# Read binary produced by encode_binary.py and verify reconstruction

def read_binary(path: str):
    with open(path, 'rb') as f:
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError('Invalid magic header')
        version = struct.unpack('<B', f.read(1))[0]
        count = struct.unpack('<I', f.read(4))[0]
        entries = []
        for _ in range(count):
            sid = struct.unpack('<I', f.read(4))[0]
            bitboards = [struct.unpack('<H', f.read(2))[0] for _ in range(8)]
            mcount = struct.unpack('<H', f.read(2))[0]
            moves = f.read(mcount)
            entries.append((sid, bitboards, moves))
        return version, entries

def reconstruct_from_moves(initial_board: str, moves: List[Tuple[int, int]]) -> List[str]:
    states = [initial_board]
    current = initial_board
    for mv in moves:
        current = apply_move(current, mv)
        states.append(current)
    return states

def verify(csv_path: str, bin_path: str) -> bool:
    # Load CSV
    with open(csv_path, 'r', newline='', encoding='utf-8', errors='ignore') as infile:
        reader = csv.DictReader(infile)
        csv_rows = list(reader)
    # Load BIN
    version, entries = read_binary(bin_path)
    if len(entries) != len(csv_rows):
        print(f"Count mismatch: BIN {len(entries)} vs CSV {len(csv_rows)}")
        return False
    ok_all = True
    for row, (sid, _bitboards, moves_bytes) in zip(csv_rows, entries):
        initial_board = row.get('board_state') or row.get('board_config') or row.get('Initial Board') or ''
        solution_path_str = row.get('solution_path') or row.get('Solution Path') or ''
        states = parse_solution_path_flexible(solution_path_str)
        moves = unpack_moves_from_bytes(moves_bytes)
        recon = reconstruct_from_moves(initial_board, moves)
        if states and recon != states:
            ok_all = False
            print(f"Mismatch for ID {sid}:")
            print(f"  expected: {states}")
            print(f"  got     : {recon}")
    return ok_all

def demo_record(csv_path: str, bin_path: str, index: Optional[int], record_id: Optional[int]) -> None:
    # Load CSV
    with open(csv_path, 'r', newline='', encoding='utf-8', errors='ignore') as infile:
        reader = csv.DictReader(infile)
        csv_rows = list(reader)
    # Load BIN
    version, entries = read_binary(bin_path)

    if index is None and record_id is not None:
        # find by ID
        for i, (sid, *_rest) in enumerate(entries):
            if sid == record_id:
                index = i
                break

    if index is None or index < 0 or index >= len(entries):
        print("Record not found for given selector")
        return

    row = csv_rows[index]
    sid, bitboards, moves_bytes = entries[index]
    initial_board = row.get('board_state') or row.get('board_config') or row.get('Initial Board') or ''
    solution_path_str = row.get('solution_path') or row.get('Solution Path') or ''
    original_states = parse_solution_path_flexible(solution_path_str)
    moves = unpack_moves_from_bytes(moves_bytes)
    recon_states = reconstruct_from_moves(initial_board, moves)

    print(f"Record index: {index}, ID: {sid}")
    print(f"Initial board: {initial_board}")
    print(f"Moves count: {len(moves)}")
    print(f"Packed moves (hex): {moves_bytes.hex()}")
    print(f"Moves (from->to): {moves}")
    print(f"Original states count: {len(original_states)}")
    print(f"Reconstructed states count: {len(recon_states)}")
    # Show first and last 2 states for brevity
    def preview(lst: List[str]) -> List[str]:
        if len(lst) <= 6:
            return lst
        return lst[:3] + ['...'] + lst[-3:]
    print("Original states (preview):", preview(original_states))
    print("Reconstructed states (preview):", preview(recon_states))
    print("Match:", original_states == recon_states if original_states else True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_path', nargs='?', default=os.path.join('solutions_csv', 'first_5_solutions.csv'))
    parser.add_argument('--bin', dest='bin_path', default=None, help='Binary file path; defaults to encoded_solutions/<csvname>.bin')
    parser.add_argument('--index', type=int, default=None, help='Record index to demo')
    parser.add_argument('--id', dest='record_id', type=int, default=None, help='Record ID to demo')
    parser.add_argument('--verify', action='store_true', help='Run full verification')
    args = parser.parse_args()

    bin_path = args.bin_path or os.path.join('encoded_solutions', os.path.splitext(os.path.basename(args.csv_path))[0] + '.bin')

    if args.verify:
        ok = verify(args.csv_path, bin_path)
        print('OK' if ok else 'FAIL')
    if args.index is not None or args.record_id is not None:
        demo_record(args.csv_path, bin_path, args.index, args.record_id)
    if not args.verify and args.index is None and args.record_id is None:
        # default to verify
        ok = verify(args.csv_path, bin_path)
        print('OK' if ok else 'FAIL') 