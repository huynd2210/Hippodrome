#!/usr/bin/env python3
import csv
import os
import struct
from typing import List, Tuple

from transform_solutions import (
    get_bitboard,
    get_knight_bitboards,
    parse_solution_path_flexible,
    moves_from_path,
    pack_moves_to_bytes,
)

MAGIC = b'HIPP'
VERSION = 1

# Record layout per entry:
# - id: uint32 LE
# - bitboards: 8 x uint16 LE (4 knights one-hot, R, B, K, x)
# - moves_count: uint16 LE
# - moves: moves_count bytes (each 1 byte, high nibble=from, low nibble=to)

def compute_bitboards(board: str) -> List[int]:
    knights = get_knight_bitboards(board)
    rooks = get_bitboard(board, 'R')
    bishops = get_bitboard(board, 'B')
    kings = get_bitboard(board, 'K')
    empty = get_bitboard(board, 'x')
    return knights + [rooks, bishops, kings, empty]

def write_binary(csv_path: str, out_path: str) -> int:
    with open(csv_path, 'r', newline='', encoding='utf-8', errors='ignore') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(MAGIC)
        f.write(struct.pack('<B', VERSION))
        f.write(struct.pack('<I', len(rows)))
        for row in rows:
            solution_id = row.get('id') or row.get('ID') or '0'
            try:
                sid = int(solution_id)
            except Exception:
                sid = 0
            initial_board = row.get('board_state') or row.get('board_config') or row.get('Initial Board') or ''
            solution_path_str = row.get('solution_path') or row.get('Solution Path') or ''
            states = parse_solution_path_flexible(solution_path_str)
            move_list: List[Tuple[int, int]] = moves_from_path(states) if len(states) > 1 else []
            bitboards = compute_bitboards(initial_board)
            # id
            f.write(struct.pack('<I', sid))
            # bitboards (uint16)
            for bb in bitboards:
                f.write(struct.pack('<H', bb & 0xFFFF))
            # moves
            packed = pack_moves_to_bytes(move_list)
            f.write(struct.pack('<H', len(packed)))
            if packed:
                f.write(packed)
    return len(rows)

if __name__ == '__main__':
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join('solutions_csv', 'first_5_solutions.csv')
    dst_name = os.path.splitext(os.path.basename(src))[0] + '.bin'
    dst = os.path.join('encoded_solutions', dst_name)
    count = write_binary(src, dst)
    print(f'Wrote {count} records to {dst}') 