# Deployment Guide for Hippodrome Solver

This guide explains how to deploy the Hippodrome Explorer to the cloud. The recommended setup is binary-backed (small, fast to load). The legacy DB-backed option remains available as an alternative.

## Architecture

- Frontend: Flask app (unified) hosted on Render or any WSGI-compatible platform
- Data (recommended): compact binary files in `encoded_solutions/*.bin` hosted on object storage/CDN
- Alternative data: SQLite databases hosted on object storage (legacy)

## Option A: Binary-backed (Recommended)

1) Upload binaries to object storage
- Files to upload:
  - `hippodrome_solutions_og.bin`
  - `hippodrome_solutions_first_column.bin`
  - `hippodrome_solutions_last_column.bin`
  - `hippodrome_solutions_corners.bin`
  - `hippodrome_solutions_center.bin`
- Suggested storage: Cloudflare R2 (public bucket) or any static CDN. Obtain public URLs for each.

2) Deploy on Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `cd frontend_explorer && gunicorn app:app --bind 0.0.0.0:$PORT`
- Environment variables:
  - `HIPPO_SOURCE=bin`
  - `BIN_URL_TOP_ROW=https://your-storage/hippodrome_solutions_og.bin`
  - `BIN_URL_FIRST_COLUMN=https://your-storage/hippodrome_solutions_first_column.bin`
  - `BIN_URL_LAST_COLUMN=https://your-storage/hippodrome_solutions_last_column.bin`
  - `BIN_URL_CORNERS=https://your-storage/hippodrome_solutions_corners.bin`
  - `BIN_URL_CENTER=https://your-storage/hippodrome_solutions_center.bin`

Notes:
- The service downloads binaries on first access and caches them on the instance’s temp directory.
- Free tiers may sleep; first request after sleep may rebuild in-memory indexes.

3) Test
- `/` main UI
- `/api/targets`
- `/api/random?target=center`
- `/api/solution/123?target=top-row`

## Option B: DB-backed (Alternative)

1) Upload SQLite DBs to object storage
- Files to upload:
  - `hippodrome_top_row.db`
  - `hippodrome_first_column.db`
  - `hippodrome_last_column.db`
  - `hippodrome_corners.db`
  - `hippodrome_center.db`
  - `targets_index.db`

2) Deploy on Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `cd frontend_explorer && gunicorn app:app --bind 0.0.0.0:$PORT`
- Environment variables:
  - `HIPPO_SOURCE=db`
  - `DB_URL_TARGETS_INDEX=https://your-storage/targets_index.db`
  - `DB_URL_TOP_ROW=https://your-storage/hippodrome_top_row.db`
  - `DB_URL_FIRST_COLUMN=https://your-storage/hippodrome_first_column.db`
  - `DB_URL_LAST_COLUMN=https://your-storage/hippodrome_last_column.db`
  - `DB_URL_CORNERS=https://your-storage/hippodrome_corners.db`
  - `DB_URL_CENTER=https://your-storage/hippodrome_center.db`

## Troubleshooting
- 404 for a target: confirm the corresponding BIN/DB URL is set and reachable.
- Slow first response: expected on cold start; indexes are built in memory.
- CORS: enabled by default.
- Unicode console errors locally: run with UTF-8 or avoid emojis in console output.
