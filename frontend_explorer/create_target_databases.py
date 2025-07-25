#!/usr/bin/env python3
"""
Create separate SQLite databases for each target configuration.
This approach allows for lazy loading and better performance.
"""

import sqlite3
import csv
import os
import sys
from pathlib import Path

def get_target_config(filename):
    """Map CSV filenames to target configurations"""
    base_name = os.path.basename(filename).lower()
    
    if 'og.csv' in base_name or 'original' in base_name:
        return {
            'name': 'top-row',
            'positions': [0, 1, 2, 3],
            'description': 'Knights must reach the top row'
        }
    elif 'first_column' in base_name:
        return {
            'name': 'first-column', 
            'positions': [0, 4, 8, 12],
            'description': 'Knights must reach the first column'
        }
    elif 'last_column' in base_name:
        return {
            'name': 'last-column',
            'positions': [3, 7, 11, 15], 
            'description': 'Knights must reach the last column'
        }
    elif 'corners' in base_name:
        return {
            'name': 'corners',
            'positions': [0, 3, 12, 15],
            'description': 'Knights must reach the corner positions'
        }
    elif 'bottom' in base_name:
        return {
            'name': 'bottom-row',
            'positions': [12, 13, 14, 15],
            'description': 'Knights must reach the bottom row'
        }
    
    return None

def create_target_database(csv_path, target_config):
    """Create a separate database for a specific target"""
    target_name = target_config['name']
    db_path = f"hippodrome_{target_name.replace('-', '_')}.db"
    
    print(f"🔄 Creating database for {target_name}...")
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create solutions table
    cursor.execute('''
        CREATE TABLE solutions (
            id INTEGER PRIMARY KEY,
            initial_board TEXT NOT NULL,
            solution_path TEXT NOT NULL,
            moves INTEGER NOT NULL,
            time_ms REAL NOT NULL
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_moves ON solutions(moves)')
    cursor.execute('CREATE INDEX idx_time ON solutions(time_ms)')
    cursor.execute('CREATE INDEX idx_board ON solutions(initial_board)')
    
    # Create metadata table
    cursor.execute('''
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    # Insert target metadata
    cursor.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('target_name', target_name))
    cursor.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('target_positions', ','.join(map(str, target_config['positions']))))
    cursor.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('target_description', target_config['description']))
    
    # Load CSV data
    row_count = 0
    batch_size = 10000
    batch_data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    solution_id = int(row['ID'])
                    initial_board = row['Initial Board'].strip()
                    solution_path = row['Solution Path'].strip()
                    moves = int(row['Moves'])
                    time_ms = float(row['Time (ms)'])
                    
                    # Validate board length
                    if len(initial_board) != 16:
                        continue
                    
                    batch_data.append((solution_id, initial_board, solution_path, moves, time_ms))
                    row_count += 1
                    
                    # Insert in batches
                    if len(batch_data) >= batch_size:
                        cursor.executemany(
                            'INSERT INTO solutions (id, initial_board, solution_path, moves, time_ms) VALUES (?, ?, ?, ?, ?)',
                            batch_data
                        )
                        batch_data = []
                        
                        if row_count % 50000 == 0:
                            print(f"📊 Processed {row_count:,} {target_name} solutions...")
                            conn.commit()
                
                except (ValueError, KeyError) as e:
                    continue
            
            # Insert remaining batch
            if batch_data:
                cursor.executemany(
                    'INSERT INTO solutions (id, initial_board, solution_path, moves, time_ms) VALUES (?, ?, ?, ?, ?)',
                    batch_data
                )
        
        # Insert total count
        cursor.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', ('total_solutions', str(row_count)))
        
        # Final commit
        conn.commit()
        
        # Get statistics
        cursor.execute('SELECT MIN(moves), MAX(moves), AVG(moves) FROM solutions WHERE moves > 0')
        min_moves, max_moves, avg_moves = cursor.fetchone()
        
        print(f"✅ Created {target_name} database:")
        print(f"   • Solutions: {row_count:,}")
        print(f"   • Move range: {min_moves} - {max_moves} (avg: {avg_moves:.1f})")
        print(f"   • Database: {db_path} ({os.path.getsize(db_path) / (1024*1024):.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating {target_name} database: {e}")
        return False
    
    finally:
        conn.close()

def create_targets_index():
    """Create a lightweight index of all available targets"""
    index_path = "targets_index.db"
    
    if os.path.exists(index_path):
        os.remove(index_path)
    
    conn = sqlite3.connect(index_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE targets (
            name TEXT PRIMARY KEY,
            positions TEXT NOT NULL,
            description TEXT NOT NULL,
            database_file TEXT NOT NULL,
            total_solutions INTEGER NOT NULL
        )
    ''')
    
    # Find all target databases
    target_dbs = []
    for filename in os.listdir('.'):
        if filename.startswith('hippodrome_') and filename.endswith('.db') and filename != index_path:
            target_dbs.append(filename)
    
    for db_file in target_dbs:
        try:
            target_conn = sqlite3.connect(db_file)
            target_cursor = target_conn.cursor()
            
            # Get metadata
            target_cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_name',))
            name = target_cursor.fetchone()[0]
            
            target_cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_positions',))
            positions = target_cursor.fetchone()[0]
            
            target_cursor.execute('SELECT value FROM metadata WHERE key = ?', ('target_description',))
            description = target_cursor.fetchone()[0]
            
            target_cursor.execute('SELECT value FROM metadata WHERE key = ?', ('total_solutions',))
            total_solutions = int(target_cursor.fetchone()[0])
            
            cursor.execute(
                'INSERT INTO targets (name, positions, description, database_file, total_solutions) VALUES (?, ?, ?, ?, ?)',
                (name, positions, description, db_file, total_solutions)
            )
            
            target_conn.close()
            
        except Exception as e:
            print(f"⚠️ Error reading {db_file}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created targets index: {index_path}")

def main():
    print("🎯 Hippodrome Target Databases Creator")
    print("=" * 50)
    
    csv_dir = "../solutions_csv"
    if not os.path.exists(csv_dir):
        print(f"❌ CSV directory not found: {csv_dir}")
        return False
    
    # Find CSV files
    csv_files = []
    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv'):
            csv_files.append(os.path.join(csv_dir, filename))
    
    if not csv_files:
        print(f"❌ No CSV files found in {csv_dir}")
        return False
    
    print(f"📁 Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        target_config = get_target_config(csv_file)
        if target_config:
            print(f"   • {os.path.basename(csv_file)} -> {target_config['name']}")
        else:
            print(f"   • {os.path.basename(csv_file)} -> Unknown target (skipping)")
    
    # Create databases
    success_count = 0
    for csv_file in csv_files:
        target_config = get_target_config(csv_file)
        if target_config:
            if create_target_database(csv_file, target_config):
                success_count += 1
            print()
    
    if success_count > 0:
        create_targets_index()
        print(f"\n🚀 Successfully created {success_count} target databases!")
        print("Ready for lazy-loading frontend!")
    else:
        print("\n❌ No databases were created successfully")
        return False
    
    return True

if __name__ == "__main__":
    if main():
        print("\n✅ Target databases ready!")
    else:
        print("\n❌ Failed to create target databases")
        sys.exit(1) 