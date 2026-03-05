# Separate Bearer Tokens & 5-Week Data Retention Guide

## Overview

The system now supports:
1. **Separate bearer tokens** for TeamBook and DataSight APIs
2. **5-week data retention** - automatically keeps only the most recent 5 weeks

---

## Configuration

### .env File Setup

Create a `.env` file with **two separate tokens**:

```env
# TeamBook API Bearer Token
TEAMBOOK_BEARER_TOKEN=your_teambook_token_here

# DataSight API Bearer Token  
DATASIGHT_BEARER_TOKEN=your_datasight_token_here

# Data Retention (keeps only last 5 weeks)
MAX_WEEKS_TO_KEEP=5

# Other settings
DB_PATH=metrics.db
SERVICE_LINE_ID=449
```

### Why Separate Tokens?

TeamBook and DataSight are different systems with different authentication:
- **TeamBook API**: Manages pod/team information
- **DataSight API**: Provides metrics (MTTR, LTTD, RF, CFR)

Each requires its own bearer token for security and access control.

---

## 5-Week Data Retention

### How It Works

Every time data is refreshed, the system:
1. Fetches current week data
2. Stores it in the database
3. **Automatically deletes data older than 5 weeks**

### Example Timeline

```
Week 1: 2025-09-01 ← Oldest kept
Week 2: 2025-09-08
Week 3: 2025-09-15
Week 4: 2025-09-22
Week 5: 2025-09-29 ← Latest
Week 6: Fetched → Week 1 deleted automatically
```

### Benefits

✅ **Consistent storage size** - Database doesn't grow indefinitely  
✅ **Relevant data only** - Focus on recent trends  
✅ **Automatic cleanup** - No manual intervention needed  
✅ **Performance** - Faster queries on smaller dataset

### Customize Retention Period

Change in `.env` file:

```env
# Keep 3 weeks instead of 5
MAX_WEEKS_TO_KEEP=3

# Keep 8 weeks
MAX_WEEKS_TO_KEEP=8
```

---

## Setup Instructions

### 1. Update .env File

```bash
# Copy example
cp .env.example .env

# Edit with your tokens
nano .env
```

Add both tokens:
```env
TEAMBOOK_BEARER_TOKEN=eyJhbGc...your_teambook_token
DATASIGHT_BEARER_TOKEN=eyJhbGc...your_datasight_token
MAX_WEEKS_TO_KEEP=5
```

### 2. Install/Update Dependencies

```bash
pip install -r requirements.txt
```

### 3. Test Configuration

```bash
# Check tokens are loaded
python -c "import config; print('TeamBook:', bool(config.TEAMBOOK_BEARER_TOKEN)); print('DataSight:', bool(config.DATASIGHT_BEARER_TOKEN))"
```

Expected output:
```
TeamBook: True
DataSight: True
```

### 4. Run Initial Fetch

```bash
python weekly_refresh.py
```

This will:
- Fetch data using both tokens
- Store in database
- Clean up old data (if any)

### 5. Verify Data Retention

```bash
python -c "from database import MetricsDatabase; db = MetricsDatabase(); import pandas as pd; weeks = pd.read_sql('SELECT DISTINCT week_date FROM weekly_metrics ORDER BY week_date DESC', db.db_path); print(f'Weeks stored: {len(weeks)}'); print(weeks)"
```

---

## Weekly Refresh with Cleanup

### Automated (Cron)

```bash
# Runs every Monday at 9 AM
# Fetches new data AND cleans up old data automatically
0 9 * * 1 cd /Users/kritikapandey/Desktop/Gamification && python3 weekly_refresh.py >> weekly_refresh.log 2>&1
```

### Manual Refresh

From dashboard:
1. Click "🔄 Refresh Data Now" in sidebar
2. System fetches with both tokens
3. Automatically keeps only last 5 weeks

From command line:
```bash
python weekly_refresh.py
```

---

## API Call Flow

```
weekly_refresh.py starts
         ↓
Loads TEAMBOOK_BEARER_TOKEN from .env
Loads DATASIGHT_BEARER_TOKEN from .env
         ↓
TeamBook API (with TeamBook token)
  → Fetches all pods under service line 449
         ↓
For each pod:
  DataSight API (with DataSight token)
    → Fetches MTTR
    → Fetches LTTD
    → Fetches Release Frequency
    → Fetches CFR
         ↓
Calculate DPI and scores
         ↓
Store in database
         ↓
Cleanup: Keep only last 5 weeks
  - Get all week_dates
  - Sort descending
  - Keep first 5
  - Delete rest
         ↓
Done!
```

---

## Troubleshooting

### Issue: "TEAMBOOK_BEARER_TOKEN not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify it has the token
grep TEAMBOOK_BEARER_TOKEN .env

# Make sure no spaces around =
# Correct: TEAMBOOK_BEARER_TOKEN=abc123
# Wrong:   TEAMBOOK_BEARER_TOKEN = abc123
```

### Issue: "DATASIGHT_BEARER_TOKEN not found"

**Solution:**
Same as above, check `.env` file has both tokens.

### Issue: More than 5 weeks showing in dashboard

**Solution:**
```bash
# Manually run cleanup
python -c "from data_fetcher import DataFetcher; import config; f = DataFetcher(config.TEAMBOOK_BEARER_TOKEN, config.DATASIGHT_BEARER_TOKEN); f.cleanup_old_data(5)"

# Or run full refresh (includes cleanup)
python weekly_refresh.py
```

### Issue: Different tokens for same API

If you accidentally swapped the tokens:
```bash
# Edit .env and swap them
nano .env

# Restart dashboard
streamlit run app.py
```

---

## Migration from Single Token

If you previously used a single `BEARER_TOKEN`:

### Option 1: Backward Compatible (Automatic)

The system automatically uses `BEARER_TOKEN` for both APIs if separate tokens aren't configured:

```env
# Old way (still works)
BEARER_TOKEN=your_token_here
```

The code will use this token for both TeamBook and DataSight.

### Option 2: Migrate to Separate Tokens (Recommended)

```env
# Remove old token
# BEARER_TOKEN=old_token

# Add separate tokens
TEAMBOOK_BEARER_TOKEN=your_teambook_token
DATASIGHT_BEARER_TOKEN=your_datasight_token
```

---

## Verification Commands

### Check Configuration
```bash
python -c "import config; print(f'TeamBook configured: {bool(config.TEAMBOOK_BEARER_TOKEN)}'); print(f'DataSight configured: {bool(config.DATASIGHT_BEARER_TOKEN)}'); print(f'Max weeks: {config.MAX_WEEKS_TO_KEEP}')"
```

### Check Database Weeks
```bash
python -c "from database import MetricsDatabase; import sqlite3; db = MetricsDatabase(); conn = sqlite3.connect(db.db_path); cursor = conn.cursor(); weeks = cursor.execute('SELECT DISTINCT week_date FROM weekly_metrics ORDER BY week_date DESC').fetchall(); print(f'Total weeks: {len(weeks)}'); [print(f'  - {w[0]}') for w in weeks]; conn.close()"
```

### Test Cleanup Function
```bash
python -c "from data_fetcher import DataFetcher; import config; f = DataFetcher(config.TEAMBOOK_BEARER_TOKEN, config.DATASIGHT_BEARER_TOKEN); f.cleanup_old_data(5)"
```

---

## Dashboard Indicators

The sidebar shows:
- ✅ **Tokens configured** - Both tokens loaded from `.env`
- 🔑 **TeamBook & DataSight** - Using separate tokens
- 🔄 **Refresh Data Now** - Fetches and cleans up
- 💡 **Data is cached for 1 hour** - Auto-refresh info
- ⏰ **Set up cron for weekly auto-refresh** - Automation reminder

---

## Security Best Practices

1. **Never commit `.env`** - Already in `.gitignore`
2. **Use separate tokens** - Better access control
3. **Rotate tokens regularly** - Update `.env` when tokens change
4. **Restrict file permissions**:
   ```bash
   chmod 600 .env
   chmod 600 metrics.db
   ```
5. **Use environment variables in production**:
   ```bash
   export TEAMBOOK_BEARER_TOKEN="token1"
   export DATASIGHT_BEARER_TOKEN="token2"
   ```

---

## Summary

| Feature | Implementation |
|---------|---------------|
| **Separate Tokens** | ✅ TeamBook + DataSight in `.env` |
| **5-Week Retention** | ✅ Automatic cleanup after each refresh |
| **Backward Compatible** | ✅ Single `BEARER_TOKEN` still works |
| **Configurable** | ✅ Change `MAX_WEEKS_TO_KEEP` in `.env` |
| **Automated** | ✅ Cleanup runs with weekly refresh |
| **Secure** | ✅ Tokens in `.env`, not in code/UI |

Your system now matches your requirement of storing **5 weeks of data** with **separate tokens** for each API! 🎉
