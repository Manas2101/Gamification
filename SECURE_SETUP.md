# Secure Setup Guide - No UI Token Input

## Security Best Practices

✅ **Bearer token stored in `.env` file** (never in code or UI)  
✅ **`.env` file excluded from git** (via `.gitignore`)  
✅ **Automated weekly refresh** (no manual intervention)  
✅ **Dashboard is read-only** (no token exposure)

---

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Bearer Token

Create a `.env` file in the project directory:

```bash
# Copy the example file
cp .env.example .env

# Edit with your token
nano .env  # or use any text editor
```

Add your bearer token to `.env`:

```env
BEARER_TOKEN=your_actual_bearer_token_here
DB_PATH=metrics.db
SERVICE_LINE_ID=449
AUTO_REFRESH_ENABLED=false
REFRESH_INTERVAL_HOURS=168
```

**Important:** Never commit `.env` to git! It's already in `.gitignore`.

### 3. Initialize Database

```bash
python setup_database.py
```

This will:
- Create the SQLite database
- Fetch initial data using token from `.env`
- Optionally backfill historical data

### 4. Set Up Weekly Automated Refresh

#### Option A: Cron (Linux/Mac) - Recommended

```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /Users/kritikapandey/Desktop/Gamification && /usr/bin/python3 weekly_refresh.py >> weekly_refresh.log 2>&1
```

#### Option B: systemd Timer (Linux)

Create `/etc/systemd/system/gamification-refresh.service`:

```ini
[Unit]
Description=DevOps Gamification Weekly Data Refresh

[Service]
Type=oneshot
User=your_username
WorkingDirectory=/Users/kritikapandey/Desktop/Gamification
ExecStart=/usr/bin/python3 weekly_refresh.py
```

Create `/etc/systemd/system/gamification-refresh.timer`:

```ini
[Unit]
Description=Weekly refresh timer for Gamification

[Timer]
OnCalendar=Mon *-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable gamification-refresh.timer
sudo systemctl start gamification-refresh.timer
```

#### Option C: Windows Task Scheduler

Create `refresh_weekly.bat`:

```batch
@echo off
cd C:\path\to\Gamification
python weekly_refresh.py >> weekly_refresh.log 2>&1
```

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly, Monday, 9:00 AM
4. Action: Start a program → `refresh_weekly.bat`

### 5. Run Dashboard

```bash
streamlit run app.py
```

The dashboard will:
- Load data from database (no token needed)
- Show cached data (refreshed hourly)
- Display refresh button (uses `.env` token)

---

## How Weekly Data Fetching Works

### Data Collection Process

```
Monday 9 AM (Cron triggers)
         ↓
weekly_refresh.py runs
         ↓
Reads BEARER_TOKEN from .env
         ↓
Calls TeamBook API → Gets all pods
         ↓
For each pod:
  Calls DataSight APIs with current month (YYYY-MM)
    - MTTR API
    - LTTD API  
    - Release Frequency API
    - CFR API
         ↓
Calculates DPI and scores
         ↓
Stores in SQLite database
         ↓
Dashboard auto-refreshes (cache expires)
```

### Weekly vs Monthly Data

The APIs use **monthly date format** (`YYYY-MM`) but provide **weekly granularity**:

- **from**: `2025-09` (September 2025)
- **to**: `2025-09` (same month)
- **Result**: Week-by-week metrics for that month

Each run fetches the **current month's data**, which includes all weeks up to now.

### Manual Refresh (if needed)

```bash
# Run the refresh script manually
python weekly_refresh.py

# Or from Python
python -c "from data_fetcher import DataFetcher; import config; DataFetcher(config.BEARER_TOKEN).refresh_current_week()"
```

---

## Security Checklist

- [ ] `.env` file created with bearer token
- [ ] `.env` is in `.gitignore` (already done)
- [ ] Bearer token has minimum required permissions
- [ ] Cron job runs as non-root user
- [ ] Database file has restricted permissions (600)
- [ ] Logs don't contain sensitive data
- [ ] Token rotation policy in place

### Set Secure Permissions

```bash
# Restrict .env file
chmod 600 .env

# Restrict database
chmod 600 metrics.db

# Restrict logs
chmod 600 weekly_refresh.log
```

---

## Monitoring

### Check Refresh Status

```bash
# View recent logs
tail -f weekly_refresh.log

# Check last refresh time
ls -lh metrics.db

# Verify data
python -c "from database import MetricsDatabase; db = MetricsDatabase(); print(f'Latest data: {db.get_latest_metrics()[\"Week\"].max()}')"
```

### Cron Job Monitoring

```bash
# Check if cron job is scheduled
crontab -l | grep gamification

# View cron logs (varies by system)
grep CRON /var/log/syslog | grep gamification
```

### Dashboard Health Check

The dashboard sidebar shows:
- ✅ Token configured (from `.env`)
- 🔄 Refresh button (uses `.env` token)
- 💡 Cache status
- ⏰ Reminder to set up cron

---

## Troubleshooting

### Issue: "BEARER_TOKEN not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify content
cat .env | grep BEARER_TOKEN

# Reload environment
source .env  # bash
```

### Issue: Cron job not running

**Solution:**
```bash
# Check cron service is running
sudo systemctl status cron

# Test the script manually
cd /Users/kritikapandey/Desktop/Gamification
python weekly_refresh.py

# Check cron logs
grep CRON /var/log/syslog
```

### Issue: "Permission denied" on database

**Solution:**
```bash
# Fix permissions
chmod 600 metrics.db
chown $USER:$USER metrics.db
```

### Issue: Old data showing in dashboard

**Solution:**
```bash
# Clear Streamlit cache
python -c "import streamlit as st; st.cache_data.clear()"

# Or click "Clear Cache" button in dashboard
```

---

## Production Deployment

### Environment Variables (Production Server)

Instead of `.env` file, use system environment variables:

```bash
# Add to ~/.bashrc or /etc/environment
export BEARER_TOKEN="your_token"
export DB_PATH="/var/lib/gamification/metrics.db"
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# Use environment variables (set in docker-compose or k8s)
ENV BEARER_TOKEN=""
ENV DB_PATH="/data/metrics.db"

# Run cron and streamlit
CMD ["sh", "-c", "cron && streamlit run app.py"]
```

### Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gamification-secrets
type: Opaque
stringData:
  bearer-token: your_bearer_token_here
```

---

## Migration from UI Token Input

If you previously entered tokens in the UI:

1. ✅ Create `.env` file with token
2. ✅ Remove token from any saved configs
3. ✅ Restart dashboard
4. ✅ Verify "Token configured" shows in sidebar
5. ✅ Test refresh button

---

## Summary

**Before (Insecure):**
- ❌ Token entered in UI
- ❌ Token visible in browser
- ❌ Manual refresh required
- ❌ Token in session state

**After (Secure):**
- ✅ Token in `.env` file
- ✅ Never exposed to UI
- ✅ Automated weekly refresh
- ✅ Read-only dashboard
- ✅ Proper git ignore
- ✅ Secure file permissions

The dashboard is now **production-ready** with proper security practices!
