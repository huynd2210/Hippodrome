# Uploading SQLite Databases to Cloudflare D1

## Important D1 Limitations
- **10GB total storage** per account (free tier)
- **100MB per database** (this is a problem for your larger DBs)
- **1MB max size per row**
- **25MB max upload per request**

## Your Database Sizes
- hippodrome_top_row.db: 228MB ❌ (too large)
- hippodrome_first_column.db: 132MB ❌ (too large)
- hippodrome_last_column.db: 133MB ❌ (too large)
- hippodrome_corners.db: 129MB ❌ (too large)
- hippodrome_center.db: 125MB ❌ (too large)
- targets_index.db: 0.01MB ✅

## Solutions

### Option 1: Split Large Databases (Recommended)
Since your databases exceed 100MB, we need to split them or reduce their size.

### Option 2: Use Cloudflare R2 Instead
R2 is better suited for large SQLite files. You can:
1. Upload SQLite files to R2
2. Use Workers to query them via HTTP

### Option 3: Reduce Database Size
Extract only essential data (e.g., first 10,000 solutions per target)

## Method 1: Using Wrangler CLI (For databases < 100MB)

```bash
# Install Wrangler globally
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create D1 database
wrangler d1 create hippodrome-targets

# Execute SQL file to create schema
wrangler d1 execute hippodrome-targets --file=./schema.sql

# Import data from local SQLite file (must be < 25MB chunks)
wrangler d1 execute hippodrome-targets --local --file=./import-data.sql
```

## Method 2: Using D1 REST API

```bash
# First, export your SQLite data to SQL statements
sqlite3 targets_index.db .dump > targets_dump.sql

# Split into smaller chunks if needed
split -l 1000 targets_dump.sql targets_chunk_

# Upload each chunk
wrangler d1 execute hippodrome-targets --file=./targets_chunk_aa
```

## Method 3: Create Smaller Demo Databases

Since your databases are too large for D1's limits, create smaller versions:

```sql
-- Extract first 1000 solutions from each database
ATTACH DATABASE 'hippodrome_top_row.db' AS source;
ATTACH DATABASE 'hippodrome_top_row_demo.db' AS demo;

CREATE TABLE demo.solutions AS 
SELECT * FROM source.solutions 
ORDER BY moves ASC 
LIMIT 1000;
```

## Recommended Approach for Your Use Case

Given the size constraints, I recommend:

1. **Use R2 for full databases** - Store complete SQLite files
2. **Use D1 for demo/subset** - Create smaller versions for demo
3. **Hybrid approach** - D1 for metadata, R2 for full data

Would you like me to:
1. Create scripts to generate smaller demo databases?
2. Show you how to use R2 with Workers instead?
3. Create a data extraction script to reduce database size?
