# Split Deployment Guide for Hippodrome Solver

This guide explains how to deploy the Hippodrome Solver with the frontend on Render (free) and databases hosted on cloud storage.

## Architecture

- **Frontend**: Flask app hosted on Render
- **Databases**: SQLite files hosted on cloud storage (Cloudflare R2, Backblaze B2, or Google Drive)

## Step 1: Upload Databases to Cloud Storage

### Option A: Cloudflare R2 (Recommended - S3-compatible)

1. Create a Cloudflare account and enable R2
2. Create a new R2 bucket (e.g., `hippodrome-databases`)
3. Upload your database files:
   - `hippodrome_top_row.db`
   - `hippodrome_first_column.db`
   - `hippodrome_last_column.db`
   - `hippodrome_corners.db`
   - `hippodrome_center.db`
   - `targets_index.db`
4. Make the bucket public or generate presigned URLs
5. Get the public URLs for each file

### Option B: Backblaze B2 (Free 10GB)

1. Create a Backblaze B2 account
2. Create a public bucket
3. Upload all database files
4. Get the friendly URLs for each file

### Option C: Google Drive (Simple but slower)

1. Upload each database to Google Drive
2. Right-click each file → "Get link" → "Anyone with the link"
3. Convert sharing links to direct download links:
   - Change `https://drive.google.com/file/d/FILE_ID/view`
   - To `https://drive.google.com/uc?export=download&id=FILE_ID`

## Step 2: Deploy Frontend to Render

1. Make sure your code is pushed to GitHub

2. Go to [render.com](https://render.com) and sign in

3. Create a new Web Service:
   - Connect your GitHub repo
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `cd frontend_explorer && gunicorn app_cloud:app`

4. Add Environment Variables in Render dashboard:
   ```
   DB_URL_TARGETS_INDEX=https://your-storage.com/targets_index.db
   DB_URL_TOP_ROW=https://your-storage.com/hippodrome_top_row.db
   DB_URL_FIRST_COLUMN=https://your-storage.com/hippodrome_first_column.db
   DB_URL_LAST_COLUMN=https://your-storage.com/hippodrome_last_column.db
   DB_URL_CORNERS=https://your-storage.com/hippodrome_corners.db
   DB_URL_CENTER=https://your-storage.com/hippodrome_center.db
   ```

5. Deploy!

## Step 3: Testing

Once deployed, test your endpoints:

- `https://your-app.onrender.com/` - Main interface
- `https://your-app.onrender.com/api/targets` - Should return available targets
- `https://your-app.onrender.com/api/random?target=top-row` - Random solution

## Performance Considerations

- First requests will be slow as databases are downloaded
- Databases are cached after first download
- Consider using a CDN for better performance
- Render free tier sleeps after 15 minutes of inactivity

## Alternative: Lightweight Version

If you want to avoid the complexity of split deployment, you can:

1. Create a demo version with only one target (e.g., top-row)
2. Limit the database to a subset of solutions
3. Keep total size under 500MB for standard deployment

## Troubleshooting

- **"Database not found"**: Check your environment variables in Render
- **Slow performance**: Normal on first request after sleep
- **CORS errors**: The app already has CORS enabled
- **Download fails**: Ensure your storage URLs are publicly accessible

## Cost

- **Render**: Free tier available
- **Cloudflare R2**: Free up to 10GB stored, 1M requests/month
- **Backblaze B2**: First 10GB free
- **Google Drive**: 15GB free
