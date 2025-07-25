#!/usr/bin/env python3
"""
Enhanced script to create SQLite database from multiple hippodrome solutions CSV files
with different target configurations.
"""

import sqlite3
import csv
import os
import sys
import re
from pathlib import Path
import glob

def parse_target_from_filename(filename):
    """Parse target information from the CSV filename"""
    # Extract just the filename from path
    name = os.path.basename(filename)
    
    # Default target
    if 'hippodrome_solutions_og.csv' in name:
        return 'top-row', [0, 1, 2, 3]
    
    # Pattern matching for different targets
    if 'first-column' in name:
        return 'first-column', [0, 4, 8, 12]
    elif 'last-column' in name:
        return 'last-column', [3, 7, 11, 15]
    elif 'bottom-row' in name:
        return 'bottom-row', [12, 13, 14, 15]
    elif 'top-row' in name:
        return 'top-row', [0, 1, 2, 3]
    
    # Try to parse custom targets like "custom-0,3,12,15"
    custom_match = re.search(r'custom-([0-9,]+)', name)
    if custom_match:
        positions_str = custom_match.group(1)
        try:
            positions = [int(x) for x in positions_str.split(',')]
            if len(positions) == 4:
                return f'custom-{positions_str}', positions
        except ValueError:
            pass
    
    # Fallback to top-row
    return 'top-row', [0, 1, 2, 3]

def create_enhanced_database():
    """Create SQLite database from multiple CSV files with target support"""
    
    # Find all solution CSV files
    csv_dir = "../solutions_csv"
    csv_files = []
    
    # Look for solution files
    patterns = [
        "hippodrome_solutions_og.csv",
        "*first-column*.csv",
        "*last-column*.csv", 
        "*bottom-row*.csv",
        "*top-row*.csv",
        "*custom-*.csv"
    ]
    
    for pattern in patterns:
        files = glob.glob(os.path.join(csv_dir, pattern))
        csv_files.extend(files)
    
    if not csv_files:
        print(f"❌ Error: No CSV files found in {csv_dir}")
        return False
    
    print(f"📁 Found {len(csv_files)} CSV files:")
    for f in csv_files:
        target_name, positions = parse_target_from_filename(f)
        print(f"   {os.path.basename(f)} -> {target_name} {positions}")
    
    db_path = "hippodrome_solutions_enhanced.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database: {db_path}")
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create enhanced solutions table with target support
    cursor.execute('''
        CREATE TABLE solutions (
            id INTEGER,
            target_name TEXT NOT NULL,
            target_positions TEXT NOT NULL,
            initial_board TEXT NOT NULL,
            solution_path TEXT NOT NULL,
            moves INTEGER NOT NULL,
            time_ms REAL NOT NULL,
            PRIMARY KEY (id, target_name)
        )
    ''')
    
    # Create indexes for fast queries
    cursor.execute('CREATE INDEX idx_target ON solutions(target_name)')
    cursor.execute('CREATE INDEX idx_moves_target ON solutions(moves, target_name)')
    cursor.execute('CREATE INDEX idx_time_target ON solutions(time_ms, target_name)')
    cursor.execute('CREATE INDEX idx_id_target ON solutions(id, target_name)')
    
    total_rows = 0
    
    # Process each CSV file
    for csv_path in csv_files:
        target_name, target_positions = parse_target_from_filename(csv_path)
        target_positions_str = ','.join(map(str, target_positions))
        
        print(f"\n🔄 Loading {target_name} data from {os.path.basename(csv_path)}...")
        
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
                        
                        batch_data.append((
                            solution_id, target_name, target_positions_str,
                            initial_board, solution_path, moves, time_ms
                        ))
                        row_count += 1
                        
                        # Insert in batches
                        if len(batch_data) >= batch_size:
                            cursor.executemany(
                                '''INSERT OR REPLACE INTO solutions 
                                   (id, target_name, target_positions, initial_board, solution_path, moves, time_ms) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
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
                        '''INSERT OR REPLACE INTO solutions 
                           (id, target_name, target_positions, initial_board, solution_path, moves, time_ms) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        batch_data
                    )
                
                print(f"✅ Loaded {row_count:,} solutions for {target_name}")
                total_rows += row_count
                
        except Exception as e:
            print(f"⚠️  Error processing {csv_path}: {e}")
            continue
    
    # Final commit
    conn.commit()
    
    # Create targets summary table
    cursor.execute('''
        CREATE TABLE targets (
            name TEXT PRIMARY KEY,
            positions TEXT NOT NULL,
            description TEXT NOT NULL,
            total_solutions INTEGER NOT NULL
        )
    ''')
    
    # Populate targets table
    cursor.execute('''
        INSERT INTO targets (name, positions, description, total_solutions)
        SELECT 
            target_name,
            target_positions,
            CASE target_name
                WHEN 'top-row' THEN 'Knights must reach the top row'
                WHEN 'bottom-row' THEN 'Knights must reach the bottom row'
                WHEN 'first-column' THEN 'Knights must reach the first column'
                WHEN 'last-column' THEN 'Knights must reach the last column'
                ELSE 'Knights must reach custom positions'
            END,
            COUNT(*)
        FROM solutions
        GROUP BY target_name, target_positions
    ''')
    
    # Verify data
    cursor.execute('SELECT COUNT(*) FROM solutions')
    total_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT target_name) FROM solutions')
    target_count = cursor.fetchone()[0]
    
    print(f"\n✅ Enhanced database created successfully!")
    print(f"📊 Statistics:")
    print(f"   Total solutions: {total_count:,}")
    print(f"   Different targets: {target_count}")
    print(f"   Database size: {os.path.getsize(db_path) / (1024*1024):.1f} MB")
    print(f"   Database file: {db_path}")
    
    # Show target breakdown
    cursor.execute('SELECT name, total_solutions FROM targets ORDER BY total_solutions DESC')
    for name, count in cursor.fetchall():
        print(f"   {name}: {count:,} solutions")
    
    conn.close()
    return True

def verify_enhanced_database():
    """Verify the enhanced database integrity"""
    db_path = "hippodrome_solutions_enhanced.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test queries
        cursor.execute('SELECT COUNT(*) FROM solutions')
        count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM targets')
        target_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT * FROM solutions LIMIT 1')
        sample = cursor.fetchone()
        
        print(f"🔍 Enhanced Database Verification:")
        print(f"   Total records: {count:,}")
        print(f"   Available targets: {target_count}")
        print(f"   Sample: ID {sample[0]}, Target: {sample[1]}, Moves: {sample[5]}")
        print(f"✅ Enhanced database verification passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🎯 Enhanced Hippodrome Solutions - Multi-Target Database Creator")
    print("=" * 65)
    
    if create_enhanced_database():
        print("\n" + "=" * 65)
        verify_enhanced_database()
        print("\n🚀 Enhanced database ready for the multi-target frontend!")
    else:
        print("\n❌ Failed to create enhanced database")
        sys.exit(1) 