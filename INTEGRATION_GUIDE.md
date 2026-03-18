# YAML Registry Integration Guide

## Overview

The gamification system has been updated to use a **YAML-based app registry** instead of the TeamBook API for pod identification. This streamlines the workflow by:

1. **Eliminating TeamBook API dependency** - Pod names come directly from YAML files
2. **Using DataSight API with pod names** - No more pod ID lookups needed
3. **Centralized app metadata** - All app configuration in one place
4. **Simplified data flow** - YAML → DataSight API → Database → Dashboard

---

## New Workflow

```
┌─────────────────┐
│  apps/*.yaml    │  ← App registry (EIM-based filenames)
│  (9594666.yaml) │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ registry_loader │  ← Loads YAML files into AppEntry objects
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ api_integration │  ← Fetches metrics using teambook names
│  (DataSight)    │     Parameters: teambookNames, teambookLevel
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  data_fetcher   │  ← Merges YAML data + API metrics
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│    database     │  ← Stores weekly metrics (keyed by EIM)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   dashboard     │  ← Displays scores and leaderboard
└─────────────────┘
```

---

## File Structure

```
Gamification/
├── apps/                          # YAML registry directory
│   ├── 9594666.yaml              # RDH app (EIM as filename)
│   └── {eim}.yaml                # Other apps
│
├── registry_loader.py            # Loads YAML files
├── api_integration.py            # DataSight API client (uses teambook names)
├── data_fetcher.py               # Orchestrates data collection
├── database.py                   # SQLite storage
├── metrics_calculator.py         # DPI scoring logic
├── app.py                        # Streamlit dashboard
│
├── config.py                     # Configuration (loads .env)
├── .env                          # API tokens (DATASIGHT_BEARER_TOKEN)
│
└── test_integration.py           # Integration test suite
```

---

## YAML Registry Format

Each app is stored as `apps/{eim}.yaml`:

```yaml
# ── IDENTITY ─────────────────────────────────────────────────
app_name: "RDH"                      # Human-readable name
eim: "9594666"                       # EIM ID (matches filename)
teambook_pods: ['RDH']               # TeamBook pod names for DataSight API
teambook_level: "4"                  # Pod level for DataSight API

# ── TEAM ─────────────────────────────────────────────────────
itso: "Rama Mohan Rao G V K"
team_lead_email: "rammohan.rao@hsbc.co.in"
release_champion: ["Bhavani Shanker Neeloju", "Kunal Umbrani"]

# ── APP CLASSIFICATION ────────────────────────────────────────
app_type: "modern"                   # modern | traditional | legacy | vendor
stack: "java-spring"                 # Tech stack
in_production: true
tier: 2                              # 1=mission-critical, 2=important, 3=standard

# ── PIPELINE FLAGS ────────────────────────────────────────────
ci_automated: true
cd_automated: true
standard_pipeline_adopted: true
git_hygiene_adopted: false
cr_auto_creation: false
zero_touch_deployment: false
automated_rollback: true
feature_flags_adopted: false
approval_gate_count: 0

# ── ACCESS & SECURITY ─────────────────────────────────────────
priv_access_for_deploy: true
priv_access_reviewed_date: ""        # YYYY-MM-DD format
sast_enabled: true
data_classification: "internal"      # public | internal | restricted | confidential

# ── COMPLIANCE ────────────────────────────────────────────────
release_page_url: ""
compliance_evidence_page: ""

# ── AI & ADOPTION ─────────────────────────────────────────────
copilot_enabled: false
ai_tools_declared: []
apis_published: false
api_count: 0
```

See `apps/9594666.yaml` for a complete template with detailed comments.

---

## Key Changes

### 1. **No TeamBook API Needed**

**Before:**
```python
# Old workflow - required TeamBook API
teambook = TeamBookAPI(teambook_token)
pods = teambook.get_pods()  # Fetch pod IDs
for pod in pods:
    metrics = datasight.get_metrics(pod['pod_id'])  # Use pod ID
```

**After:**
```python
# New workflow - uses YAML registry
from registry_loader import RegistryLoader
loader = RegistryLoader()
apps = loader.load_all()  # Load from YAML
for app in apps:
    metrics = datasight.get_metrics(
        teambook_name=app.teambook_pods[0],  # Use pod name
        teambook_level=app.teambook_level     # Use level from YAML
    )
```

### 2. **DataSight API Parameters Changed**

**Before:**
```python
params = {
    'teambookIds': 12345,          # Pod ID (integer)
    'teambookLevel': 5             # Hardcoded level
}
```

**After:**
```python
params = {
    'teambookNames': 'RDH',        # Pod name (string from YAML)
    'teambookLevel': '4'           # Level from YAML
}
```

### 3. **RF Metric Field**

**Before:** `releases`  
**After:** `ytd_pdptppy_basis` (with fallback to `releases`)

### 4. **DataFetcher Initialization**

**Before:**
```python
fetcher = DataFetcher(
    teambook_token="...",
    datasight_token="..."
)
```

**After:**
```python
fetcher = DataFetcher(
    datasight_token="..."  # Only DataSight token needed
)
```

---

## Usage

### 1. **Add a New App**

Create `apps/{eim}.yaml`:

```bash
cp apps/9594666.yaml apps/1234567.yaml
# Edit the file with your app's details
```

### 2. **Configure API Token**

Edit `.env`:

```bash
DATASIGHT_BEARER_TOKEN=your_token_here
```

### 3. **Fetch Weekly Data**

```bash
python3 weekly_refresh.py
```

Or programmatically:

```python
from data_fetcher import DataFetcher
import config

fetcher = DataFetcher(config.DATASIGHT_BEARER_TOKEN)
fetcher.refresh_current_week()
```

### 4. **Run Dashboard**

```bash
streamlit run app.py
```

### 5. **Test Integration**

```bash
python3 test_integration.py
```

---

## Testing

The `test_integration.py` script verifies:

1. ✅ **Registry Loader** - YAML files load correctly
2. ⚠️ **API Integration** - DataSight API calls work (requires token)
3. ✅ **Database Storage** - Metrics store and retrieve correctly
4. ⚠️ **Complete Flow** - End-to-end integration (requires token)

**Test Results:**
```
Registry Loader: ✅ PASS
API Integration: ⚠️ SKIP (no token configured)
Database Storage: ✅ PASS
Complete Flow: ⚠️ SKIP (no token configured)
```

To run full tests, configure `DATASIGHT_BEARER_TOKEN` in `.env`.

---

## Database Schema

Apps are stored with **EIM as pod_id**:

```sql
-- Pods table
CREATE TABLE pods (
    pod_id INTEGER PRIMARY KEY,      -- EIM ID (e.g., 9594666)
    pod_name TEXT NOT NULL,          -- App name (e.g., "RDH")
    stack TEXT,
    business_unit TEXT,
    tier TEXT
);

-- Weekly metrics table
CREATE TABLE weekly_metrics (
    id INTEGER PRIMARY KEY,
    pod_id INTEGER NOT NULL,         -- EIM ID
    week_date DATE NOT NULL,
    week_start DATE NOT NULL,
    rf INTEGER,                      -- From ytd_pdptppy_basis
    lttd REAL,
    cfr REAL,
    mttr REAL,
    -- ... scores and flags ...
    dpi INTEGER,
    FOREIGN KEY (pod_id) REFERENCES pods (pod_id)
);
```

---

## Troubleshooting

### Issue: "No apps loaded from registry"

**Solution:** Check that YAML files exist in `apps/` directory:

```bash
ls -la apps/*.yaml
```

### Issue: "DATASIGHT_BEARER_TOKEN not configured"

**Solution:** Create `.env` file:

```bash
echo "DATASIGHT_BEARER_TOKEN=your_token_here" > .env
```

### Issue: "Error parsing YAML file"

**Solution:** Validate YAML syntax:

```bash
python3 -c "import yaml; yaml.safe_load(open('apps/9594666.yaml'))"
```

### Issue: "API returns empty data"

**Possible causes:**
- Invalid teambook pod name
- Wrong teambook level
- No data for the requested time period

**Debug:**
```python
from api_integration import DataSightAPI
from datetime import datetime

api = DataSightAPI("your_token")
data = api.get_all_metrics("RDH", "4", datetime.now(), datetime.now())
print(data)
```

---

## Migration Checklist

- [x] Create `apps/` directory
- [x] Create YAML files for all apps (format: `{eim}.yaml`)
- [x] Update `registry_loader.py` to parse new fields
- [x] Update `api_integration.py` to use teambook names
- [x] Update `data_fetcher.py` to use YAML registry
- [x] Fix `database.py` syntax error
- [x] Test registry loader
- [x] Test database storage
- [ ] Configure DataSight API token in `.env`
- [ ] Test API integration with real token
- [ ] Populate YAML files for all production apps
- [ ] Update scoring formulas (if needed)
- [ ] Deploy to production

---

## Next Steps

1. **Configure API Token** - Add `DATASIGHT_BEARER_TOKEN` to `.env`
2. **Create YAML Files** - Add all production apps to `apps/` directory
3. **Test with Real Data** - Run `python3 test_integration.py`
4. **Update Scoring** - Integrate new formulas from `scoring_updated.py` (if needed)
5. **Deploy Dashboard** - Run `streamlit run app.py`

---

## Support

For issues or questions:
- Check `test_integration.py` output for diagnostics
- Review YAML syntax in `apps/*.yaml`
- Verify API token configuration in `.env`
- Check logs in `weekly_refresh.log`



# quick_populate.py
from data_fetcher import DataFetcher
import config

# Initialize with DataSight token only
fetcher = DataFetcher(
    datasight_token=config.DATASIGHT_BEARER_TOKEN,
    db_path=config.DB_PATH
)

# Fetch current week data from YAML apps
fetcher.refresh_current_week()

print("✅ Database populated!")