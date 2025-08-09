"""
This script provides functions for transforming board states and solution paths
into more compact representations, such as bitboards and packed move lists.
These transformations are used to reduce the size of the solution data.
"""
import csv
import json
import os
import base64
from typing import List, Tuple

def szudzik_pairing(x, y):
    """Applies the Szudzik pairing function to two unsigned integers."""
    x = int(x)
    y = int(y)
    return (x * x + x + y) if x >= y else (y * y + x)

def recursive_pair(numbers):
    """Recursively applies the Szudzik pairing function to a list of numbers."""
    if len(numbers) < 2:
        raise ValueError("Recursive pairing requires at least two numbers.")
    
    result = szudzik_pairing(numbers[0], numbers[1])
    for i in range(2, len(numbers)):
        result = szudzik_pairing(result, numbers[i])
    return result

def get_bitboard(board_string, piece):
    """Creates a 16-bit integer bitboard for a given piece or for all pieces of a type."""
    bitboard = 0
    for i, char in enumerate(board_string):
        if char == piece:
            bitboard |= 1 << i
    return bitboard

def get_knight_bitboards(board_string):
    """Gets individual bitboards for up to four knights."""
    knight_indices = [i for i, char in enumerate(board_string) if char == 'N']
    knight_bitboards = [0, 0, 0, 0]
    for i, index in enumerate(knight_indices):
        if i < 4:
            knight_bitboards[i] = 1 << index
    return knight_bitboards

def parse_board_to_hash(board_string):
    """
    Parses a board string into 8 bitboards and then hashes them into a single number.
    The 8 bitboards are: 4 for knights, 1 for rooks, 1 for bishops, 1 for kings, 1 for empty.
    """
    knight_bbs = get_knight_bitboards(board_string)
    rooks_bb = get_bitboard(board_string, 'R')
    bishops_bb = get_bitboard(board_string, 'B')
    kings_bb = get_bitboard(board_string, 'K')
    empty_bb = get_bitboard(board_string, 'x')
    
    # The order is important for reversing the hash if ever needed.
    all_bitboards = knight_bbs + [rooks_bb, bishops_bb, kings_bb, empty_bb]
    
    return recursive_pair(all_bitboards)

def get_move_from_states(prev_state, next_state):
    """Compares two board states to find the move (from, to)."""
    from_pos, to_pos = -1, -1
    moved_piece = ''

    for i in range(len(prev_state)):
        if prev_state[i] != next_state[i]:
            if prev_state[i] == 'x':
                # The empty square in the previous state is the 'to' position
                to_pos = i
                moved_piece = next_state[i]
            elif next_state[i] == 'x':
                 # The empty square in the next state is the 'from' position
                from_pos = i

    # A sanity check in case logic is flawed
    if from_pos == -1 or to_pos == -1:
        # This can happen if the solution path is just one state (no moves)
        if prev_state == next_state and "no solution" not in prev_state.lower():
             return None # No move occurred
        return None

    return [from_pos, to_pos]

# --- New helpers for flexible parsing and packing ---

def parse_solution_path_flexible(solution_path_raw: str) -> List[str]:
    """Parse solution path from JSON array or semicolon-separated string."""
    if not solution_path_raw:
        return []
    # Try JSON array first
    try:
        parsed = json.loads(solution_path_raw)
        if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
            return parsed
    except json.JSONDecodeError:
        pass
    # Fallback: semicolon-separated
    if ';' in solution_path_raw:
        return [s.strip() for s in solution_path_raw.split(';') if s.strip()]
    # Single state or unsupported format
    s = solution_path_raw.strip()
    return [s] if s else []

def moves_from_path(states: List[str]) -> List[Tuple[int, int]]:
    """Compute (from,to) moves by diffing consecutive board states."""
    moves: List[Tuple[int, int]] = []
    for i in range(len(states) - 1):
        mv = get_move_from_states(states[i], states[i + 1])
        if isinstance(mv, list) and len(mv) == 2:
            moves.append((int(mv[0]), int(mv[1])))
    return moves

def pack_moves_to_bytes(moves: List[Tuple[int, int]]) -> bytes:
    """Pack moves into bytes: 1 byte per move (high nibble=from, low nibble=to)."""
    packed = bytearray()
    for from_pos, to_pos in moves:
        packed.append(((from_pos & 0x0F) << 4) | (to_pos & 0x0F))
    return bytes(packed)

def unpack_moves_from_bytes(data: bytes) -> List[Tuple[int, int]]:
    """Unpack 1-byte-per-move format into list of (from,to)."""
    result: List[Tuple[int, int]] = []
    for b in data:
        result.append(((b >> 4) & 0x0F, b & 0x0F))
    return result

def apply_move(board: str, move: Tuple[int, int]) -> str:
    """Apply a single (from,to) move to a board string and return new board."""
    from_pos, to_pos = move
    if not (0 <= from_pos < 16 and 0 <= to_pos < 16):
        return board
    board_list = list(board)
    board_list[to_pos] = board_list[from_pos]
    board_list[from_pos] = 'x'
    return ''.join(board_list)

def verify_moves_against_path(initial_board: str, moves: List[Tuple[int, int]], path: List[str]) -> bool:
    """Verify moves reconstruct the provided path (if path has multiple states)."""
    if len(path) <= 1:
        return True
    current = initial_board
    for i, mv in enumerate(moves):
        current = apply_move(current, mv)
        # Optionally compare against given path state if length matches
        if i + 1 < len(path) and path[i + 1] != current:
            return False
    return True


def transform_solutions(input_file, output_file):
    """
    Reads a CSV with string solutions, transforms them, and writes to a new CSV.
    """
    print(f"Processing {input_file}...")
    
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['id', 'board_config', 'board_hash', 'moves_count', 'moves_b64']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # Input flexibility for column names
            solution_id = row.get('id') or row.get('ID')
            board_config = row.get('board_state') or row.get('board_config') or row.get('Initial Board')
            solution_path_str = row.get('solution_path') or row.get('Solution Path') or ''

            # Handle cases where board_config might be None or empty
            if not board_config:
                print(f"Skipping row with empty board_config (ID: {solution_id}).")
                continue

            # Parse solution path flexibly
            solution_path = parse_solution_path_flexible(solution_path_str)

            # 1. Compute hash of the initial board (Szudzik over bitboards)
            board_hash = parse_board_to_hash(board_config)

            # 2. Compute compact moves list
            move_list: List[Tuple[int, int]] = []
            if len(solution_path) > 1:
                move_list = moves_from_path(solution_path)

            # 3. Pack moves and encode for CSV
            packed_bytes = pack_moves_to_bytes(move_list)
            moves_b64 = base64.b64encode(packed_bytes).decode('ascii') if packed_bytes else ''

            # 4. Optional verification when path available
            if solution_path and move_list and len(move_list) == len(solution_path) - 1:
                ok = verify_moves_against_path(board_config, move_list, solution_path)
                if not ok:
                    print(f"Warning: verification failed for ID {solution_id}")

            # Write the transformed row
            writer.writerow({
                'id': solution_id,
                'board_config': board_config,
                'board_hash': board_hash,
                'moves_count': len(move_list),
                'moves_b64': moves_b64,
            })

    print(f"Finished processing. Output saved to {output_file}")

def main():
    """Main function to transform all solution CSVs in the solutions_csv directory."""
    input_dir = 'C:\Woodchop\hippodrome-solver-github\solutions_csv'
    output_dir = 'C:\Woodchop\hippodrome-solver-github\encoded_solutions'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            input_path = os.path.join(input_dir, filename)
            output_filename = f"encoded_{filename}"
            output_path = os.path.join(output_dir, output_filename)
            transform_solutions(input_path, output_path)

if __name__ == '__main__':
    main()