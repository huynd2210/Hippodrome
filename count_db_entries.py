#!/usr/bin/env python3
import os
import sqlite3

dbs = [
    'hippodrome_top_row.db',
    'hippodrome_first_column.db',
    'hippodrome_last_column.db',
    'hippodrome_corners.db',
    'hippodrome_center.db',
]

for db in dbs:
    if not os.path.exists(db):
        print(f"{db}: missing")
        continue
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM solutions')
        n = cur.fetchone()[0]
        conn.close()
        print(f"{db}: {n}")
    except Exception as e:
        print(f"{db}: error - {e}") 