# Real-Time API Integration Guide

## Overview

This integration connects your DevOps Gamification Dashboard to:
- **TeamBook API**: Fetches pod details (pod ID and names)
- **DataSight API**: Fetches metrics (MTTR, LTTD, RF, CFR)

Data is stored in a SQLite database for historical tracking and trend analysis.

## Architecture

```
TeamBook API → Pod Details
                    ↓
DataSight API → Metrics (MTTR, LTTD, RF, CFR)
                    ↓
Metrics Calculator → DPI & Scores
                    ↓
SQLite Database → Historical Storage
                    ↓
Streamlit Dashboard → Visualization
```

## Files Created

1. **`api_integration.py`**: API client classes for TeamBook and DataSight
2. **`database.py`**: SQLite database operations
3. **`metrics_calculator.py`**: DPI and score calculation logic
4. **`data_fetcher.py`**: Orchestrates data fetching workflow
5. **`streamlit_integration.py`**: Streamlit-specific data loading
6. **`config.py`**: Configuration settings

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Bearer Token

**Option A: Environment Variable (Recommended)**
```bash
export BEARER_TOKEN="your_bearer_token_here"
```

**Option B: Direct in Dashboard**
- Enter token in the sidebar "Bearer Token" field

### 3. Initialize Database

Run the data fetcher to create the database and fetch initial data:

```bash
python data_fetcher.py
```

Or use the interactive setup:

```bash
python setup_database.py
```

### 4. Run Dashboard

```bash
streamlit run app.py
```

## Usage

### Fetching Data

#### From Dashboard (Recommended)
1. Open the dashboard
2. Enter your Bearer Token in the sidebar
3. Click "🔄 Refresh Data"

#### From Command Line
```python
from data_fetcher import DataFetcher

# Initialize with your token
fetcher = DataFetcher("your_bearer_token")

# Fetch current week
fetcher.refresh_current_week()

# Backfill historical data (3 months)
fetcher.backfill_historical_data(months=3)
```

### Weekly Data Format

The APIs expect dates in `YYYY-MM` format. For weekly data:
- `from` and `to` parameters use the same date (e.g., `2025-09`)
- This represents the week/month for which metrics are calculated

### API Endpoints

**TeamBook API**
```
GET https://api-teambook.global.hsbc/pod?serviceline=449
```

**DataSight APIs**
```
GET https://datasight.global.hsbc/incident/metric/mttr/by-group/teambook/metric
GET https://datasight.global.hsbc/releases/metric/lttd/teambook/metric
GET https://datasight.global.hsbc/releases/metric/release-frequency/teambook/metric
GET https://datasight.global.hsbc/releases/metric/cfr/teambook/metric
```

## Database Schema

### Pods Table
- `pod_id`: Primary key
- `pod_name`: Pod name
- `stack`: Technology stack (Legacy/Cloud Native/Hybrid)
- `business_unit`: Business unit
- `tier`: Performance tier

### Weekly Metrics Table
- `pod_id`: Foreign key to pods
- `week_date`: Week date (YYYY-MM-DD)
- `rf`: Release Frequency
- `lttd`: Lead Time to Deploy
- `cfr`: Change Failure Rate
- `mttr`: Mean Time to Restore
- `dpi`: DevOps Performance Index
- Plus all calculated scores and flags

## DPI Calculation

DPI is calculated from 7 components:

1. **RF Score** (5-35): Based on release frequency
2. **Flow Score** (5-25): Based on LTTD (capped if measurability < 90%)
3. **CFR Score** (1-7): Based on change failure rate
4. **MTTR Score** (1-7): Based on mean time to restore
5. **Priv Score** (0-6): Based on privileged access count
6. **Automation Score** (0-20): Based on CI/CD/IaC/Rollback/Self-Service
7. **Stability Score** (0-20): Based on reporting and performance

**Total DPI** = Sum of all component scores

### Tier Classification
- **Elite**: DPI ≥ 85
- **Advanced**: DPI ≥ 70
- **Emerging**: DPI ≥ 50
- **Needs Support**: DPI < 50

## Randomized Fields

Fields not available from APIs are randomized for now:
- `ltdd_measurable`: 0.85-1.0
- `priv_access`: 0-3
- `ci`, `cd`, `iac`, `rollback`, `self_service`: Boolean
- `stack`: Legacy/Cloud Native/Hybrid
- `business_unit`: BU A/B/C

## Troubleshooting

### No Data Showing
1. Check bearer token is valid
2. Verify API connectivity
3. Check database file exists: `metrics.db`
4. Review logs for errors

### API Errors
- Ensure bearer token has correct permissions
- Verify service line ID (449) is correct
- Check network connectivity to HSBC APIs

### Database Issues
```python
from database import MetricsDatabase

db = MetricsDatabase()
pods = db.get_all_pods()
print(f"Total pods: {len(pods)}")

latest = db.get_latest_metrics()
print(f"Latest metrics: {len(latest)}")
```

## Scheduled Refresh

To set up weekly automatic refresh, use cron:

```bash
# Add to crontab (runs every Monday at 9 AM)
0 9 * * 1 cd /path/to/Gamification && python -c "from data_fetcher import DataFetcher; DataFetcher('$BEARER_TOKEN').refresh_current_week()"
```

## Security Notes

- **Never commit bearer tokens** to version control
- Use environment variables for sensitive data
- Rotate tokens regularly
- Restrict database file permissions

## Next Steps

1. ✅ Set up bearer token
2. ✅ Run initial data fetch
3. ✅ Verify data in dashboard
4. 🔄 Set up weekly refresh schedule
5. 📊 Monitor trends over time

## Support

For issues or questions:
1. Check logs in console output
2. Verify API responses
3. Review database contents
4. Check configuration in `config.py`
