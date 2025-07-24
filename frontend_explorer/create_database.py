#!/usr/bin/env python3
"""
Script to create SQLite database from the hippodrome solutions CSV file.
This provides much better performance than loading 209MB CSV into memory.
"""

import sqlite3
import csv
import os
import sys
from pathlib import Path

def create_hippodrome_database():
    """Create SQLite database from the solutions CSV file"""
    
    # Paths
    csv_path = "../solutions_csv/hippodrome_solutions_og.csv"
    db_path = "hippodrome_solutions.db"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        return False
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database: {db_path}")
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create solutions table with optimized schema
    cursor.execute('''
        CREATE TABLE solutions (
            id INTEGER PRIMARY KEY,
            initial_board TEXT NOT NULL,
            solution_path TEXT NOT NULL,
            moves INTEGER NOT NULL,
            time_ms REAL NOT NULL
        )
    ''')
    
    # Create indexes for fast queries
    cursor.execute('CREATE INDEX idx_moves ON solutions(moves)')
    cursor.execute('CREATE INDEX idx_time ON solutions(time_ms)')
    cursor.execute('CREATE INDEX idx_id ON solutions(id)')
    
    print(f"🔄 Loading CSV data from {csv_path}...")
    
    # Load CSV data into database
    row_count = 0
    batch_size = 10000
    batch_data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Clean and validate data
                try:
                    solution_id = int(row['ID'])
                    initial_board = row['Initial Board'].strip()
                    solution_path = row['Solution Path'].strip()
                    moves = int(row['Moves'])
                    time_ms = float(row['Time (ms)'])
                    
                    # Validate board length
                    if len(initial_board) != 16:
                        print(f"⚠️  Skipping invalid board (ID {solution_id}): length {len(initial_board)}")
                        continue
                    
                    batch_data.append((solution_id, initial_board, solution_path, moves, time_ms))
                    row_count += 1
                    
                    # Insert in batches for better performance
                    if len(batch_data) >= batch_size:
                        cursor.executemany(
                            'INSERT INTO solutions (id, initial_board, solution_path, moves, time_ms) VALUES (?, ?, ?, ?, ?)',
                            batch_data
                        )
                        batch_data = []
                        
                        if row_count % 50000 == 0:
                            print(f"📊 Processed {row_count:,} solutions...")
                            conn.commit()
                
                except (ValueError, KeyError) as e:
                    print(f"⚠️  Skipping invalid row: {e}")
                    continue
            
            # Insert remaining batch
            if batch_data:
                cursor.executemany(
                    'INSERT INTO solutions (id, initial_board, solution_path, moves, time_ms) VALUES (?, ?, ?, ?, ?)',
                    batch_data
                )
        
        # Final commit
        conn.commit()
        
        # Verify data
        cursor.execute('SELECT COUNT(*) FROM solutions')
        total_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(moves), MAX(moves), AVG(moves) FROM solutions')
        min_moves, max_moves, avg_moves = cursor.fetchone()
        
        cursor.execute('SELECT MIN(time_ms), MAX(time_ms), AVG(time_ms) FROM solutions')
        min_time, max_time, avg_time = cursor.fetchone()
        
        print(f"\n✅ Database created successfully!")
        print(f"📊 Statistics:")
        print(f"   Total solutions: {total_count:,}")
        print(f"   Move range: {min_moves} - {max_moves} (avg: {avg_moves:.1f})")
        print(f"   Time range: {min_time:.2f} - {max_time:.2f}ms (avg: {avg_time:.2f}ms)")
        print(f"   Database size: {os.path.getsize(db_path) / (1024*1024):.1f} MB")
        print(f"   Database file: {db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return False
    
    finally:
        conn.close()

def verify_database():
    """Verify the database integrity"""
    db_path = "hippodrome_solutions.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test some queries
        cursor.execute('SELECT COUNT(*) FROM solutions')
        count = cursor.fetchone()[0]
        
        cursor.execute('SELECT * FROM solutions LIMIT 1')
        sample = cursor.fetchone()
        
        cursor.execute('SELECT id, moves FROM solutions ORDER BY moves DESC LIMIT 1')
        hardest = cursor.fetchone()
        
        cursor.execute('SELECT id, moves FROM solutions ORDER BY moves ASC LIMIT 1')
        easiest = cursor.fetchone()
        
        print(f"🔍 Database Verification:")
        print(f"   Total records: {count:,}")
        print(f"   Sample record: ID {sample[0]}, Board: {sample[1][:20]}..., Moves: {sample[3]}")
        print(f"   Hardest puzzle: ID {hardest[0]} ({hardest[1]} moves)")
        print(f"   Easiest puzzle: ID {easiest[0]} ({easiest[1]} moves)")
        print(f"✅ Database verification passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🎯 Hippodrome Solutions - SQLite Database Creator")
    print("=" * 55)
    
    if create_hippodrome_database():
        print("\n" + "=" * 55)
        verify_database()
        print("\n🚀 Database ready for the frontend explorer!")
    else:
        print("\n❌ Failed to create database")
        sys.exit(1) 