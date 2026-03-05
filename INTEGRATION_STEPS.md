# Integration Steps - Connecting Database to Dashboard

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python setup_database.py
```
Follow the prompts to:
- Enter your bearer token
- Fetch initial data
- Optionally backfill historical data

### Step 3: Update app.py (Optional)

To use the database instead of CSV, add these lines at the top of `app.py`:

```python
# Add after existing imports (around line 11)
from streamlit_integration import load_dashboard_data, show_data_refresh_section

# Replace the load_history() section (around line 1368) with:
latest_df, history_df = load_dashboard_data()

# Add refresh controls in sidebar (add anywhere in sidebar section):
show_data_refresh_section()
```

## Detailed Integration Options

### Option A: Minimal Integration (Keep CSV as fallback)

Keep your existing code and add database as an option:

```python
import os
from streamlit_integration import DashboardDataLoader

# Try loading from database first, fallback to CSV
try:
    loader = DashboardDataLoader()
    history_df = loader.load_historical_metrics()
    if history_df.empty:
        raise ValueError("No database data")
except:
    # Fallback to CSV
    history_df = load_history()
```

### Option B: Full Database Integration (Recommended)

Replace CSV loading completely:

1. **Backup your current app.py**
```bash
cp app.py app.py.backup
```

2. **Add imports at top of app.py** (after line 11):
```python
from streamlit_integration import load_dashboard_data, show_data_refresh_section
```

3. **Replace data loading section** (around line 1354-1368):
```python
# OLD CODE (comment out or remove):
# def load_history():
#     if os.path.exists(HISTORY_FILE):
#         hist = pd.read_csv(HISTORY_FILE, parse_dates=['Week','Week_Start'])
#         return hist
#     else:
#         return create_sample_history(HISTORY_FILE)
# 
# history_df = load_history()

# NEW CODE:
latest_df, history_df = load_dashboard_data()
```

4. **Add refresh controls in sidebar** (around line 1450 or in sidebar section):
```python
# Add data refresh section
show_data_refresh_section()
```

### Option C: Hybrid Approach (Use both)

Use database for real-time data, keep CSV for backup:

```python
from streamlit_integration import DashboardDataLoader

# Load from database
loader = DashboardDataLoader()
db_data = loader.load_latest_metrics()

if not db_data.empty:
    # Use database data
    history_df = loader.load_historical_metrics()
    st.sidebar.success("📊 Using real-time data")
else:
    # Fallback to CSV
    history_df = load_history()
    st.sidebar.warning("📁 Using CSV data (no database)")

# Add refresh option
show_data_refresh_section()
```

## Testing the Integration

### 1. Test Database Connection
```python
python -c "from database import MetricsDatabase; db = MetricsDatabase(); print('✅ Database OK')"
```

### 2. Test Data Fetching (requires bearer token)
```python
python example_usage.py
```

### 3. Test Dashboard
```bash
streamlit run app.py
```

## Data Flow

```
User enters Bearer Token in Dashboard
           ↓
Click "Refresh Data" button
           ↓
TeamBook API → Fetch all pods
           ↓
For each pod:
  DataSight API → Fetch MTTR, LTTD, RF, CFR
           ↓
Randomize missing fields (stack, BU, etc.)
           ↓
Calculate DPI and scores
           ↓
Store in SQLite database
           ↓
Dashboard displays updated data
```

## Weekly Refresh Schedule

### Manual Refresh
- Click "🔄 Refresh Data" in dashboard sidebar
- Enter bearer token when prompted

### Automated Refresh (Cron)

**Linux/Mac:**
```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /Users/kritikapandey/Desktop/Gamification && /usr/bin/python3 -c "from data_fetcher import DataFetcher; import os; DataFetcher(os.getenv('BEARER_TOKEN')).refresh_current_week()" >> /tmp/gamification_refresh.log 2>&1
```

**Windows (Task Scheduler):**
Create a batch file `refresh_data.bat`:
```batch
@echo off
cd C:\path\to\Gamification
python -c "from data_fetcher import DataFetcher; import os; DataFetcher(os.getenv('BEARER_TOKEN')).refresh_current_week()"
```

Then schedule it in Task Scheduler to run weekly.

## Troubleshooting

### Issue: "No module named 'api_integration'"
**Solution:** Make sure you're in the correct directory
```bash
cd /Users/kritikapandey/Desktop/Gamification
python app.py
```

### Issue: "Database is locked"
**Solution:** Close any other processes accessing the database
```bash
# Find processes using the database
lsof metrics.db
# Kill if needed
```

### Issue: "Invalid bearer token"
**Solution:** 
1. Verify token is correct
2. Check token hasn't expired
3. Ensure token has proper permissions for both APIs

### Issue: "No data showing in dashboard"
**Solution:**
```python
# Check database contents
python -c "from database import MetricsDatabase; db = MetricsDatabase(); print(db.get_latest_metrics())"
```

## File Structure

```
Gamification/
├── app.py                          # Main dashboard (existing)
├── api_integration.py              # NEW: API clients
├── database.py                     # NEW: Database operations
├── metrics_calculator.py           # NEW: Score calculations
├── data_fetcher.py                 # NEW: Data orchestrator
├── streamlit_integration.py        # NEW: Streamlit helpers
├── config.py                       # NEW: Configuration
├── setup_database.py               # NEW: Setup script
├── example_usage.py                # NEW: Examples
├── metrics.db                      # NEW: SQLite database (created on first run)
├── metrics_history.csv             # OLD: CSV backup (keep for now)
├── requirements.txt                # UPDATED: Added requests
└── README_API_INTEGRATION.md       # NEW: Full documentation
```

## Next Steps

1. ✅ **Setup Complete** - You've created all necessary files
2. 🔄 **Test Integration** - Run `python setup_database.py`
3. 🎯 **Update Dashboard** - Choose integration option (A, B, or C)
4. 📊 **Verify Data** - Check dashboard shows real data
5. ⏰ **Schedule Refresh** - Set up weekly automation
6. 🚀 **Go Live** - Share with team!

## Support Commands

```bash
# Check database status
python -c "from database import MetricsDatabase; db = MetricsDatabase(); pods = db.get_all_pods(); print(f'Pods: {len(pods)}'); metrics = db.get_latest_metrics(); print(f'Metrics: {len(metrics)}')"

# Manually refresh data
python -c "from data_fetcher import DataFetcher; DataFetcher('YOUR_TOKEN').refresh_current_week()"

# Clear cache
python -c "import streamlit as st; st.cache_data.clear()"

# View logs
tail -f /tmp/gamification_refresh.log
```
