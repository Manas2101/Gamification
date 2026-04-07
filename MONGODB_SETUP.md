# MongoDB Integration Guide

## Overview

The platform now supports **MongoDB** as an alternative to SQLite for data storage. MongoDB provides better scalability, performance, and flexibility for production deployments.

---

## 🚀 Quick Start

### 1. Install MongoDB Driver

```bash
pip install pymongo
```

### 2. Set MongoDB Connection String

Add to your `.env` file:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=devops_metrics
```

**For MongoDB Atlas (Cloud):**
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=devops_metrics
```

### 3. Run the Platform

The platform will automatically detect MongoDB configuration and use it instead of SQLite:

```bash
python main.py refresh
```

---

## 📊 MongoDB Collections

The platform creates two main collections:

### 1. **pods** Collection
Stores pod/application metadata:
```json
{
  "pod_id": "123456",
  "pod_name": "My Application",
  "stack": "Java",
  "business_unit": "Engineering",
  "tier": "1",
  "created_at": ISODate("2026-04-07T..."),
  "updated_at": ISODate("2026-04-07T...")
}
```

**Indexes:**
- `pod_id` (unique)

### 2. **metrics** Collection
Stores weekly metrics snapshots:
```json
{
  "pod_id": "123456",
  "week_date": "2026-04-07",
  "rf": 280,
  "lttd": 1.8,
  "git_hygiene_score": 95.0,
  "Release_Velocity_Score": 100.0,
  "Git_Hygiene_Score": 95.0,
  "Pipeline_Maturity_Score": 100.0,
  "Compliance_Score": 100.0,
  "Quality_Security_Score": 100.0,
  "Adoption_Score": 100.0,
  "dpi": 98.5,
  "apis_published_iadp": true,
  "apis_published_apix": true,
  "ai_devops_onboarded": true,
  "created_at": ISODate("2026-04-07T...")
}
```

**Indexes:**
- `pod_id` + `week_date` (compound, descending)
- `created_at` (descending)

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | MongoDB connection string | - | Yes (for MongoDB) |
| `MONGODB_DATABASE` | Database name | `devops_metrics` | No |

### Connection String Formats

**Local MongoDB:**
```
mongodb://localhost:27017
```

**With Authentication:**
```
mongodb://username:password@localhost:27017
```

**MongoDB Atlas:**
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

**Replica Set:**
```
mongodb://host1:27017,host2:27017,host3:27017/?replicaSet=myReplicaSet
```

---

## 🎯 Usage in Code

### Automatic Detection

The platform automatically detects MongoDB configuration:

```python
from src.utils.config import Config

config = Config()

if config.use_mongodb:
    from src.data.mongodb import MongoDatabase
    db = MongoDatabase(config.mongodb_uri, config.mongodb_database)
else:
    from src.data.database import Database
    db = Database(config.db_path)
```

### Direct Usage

```python
from src.data.mongodb import MongoDatabase

# Initialize
db = MongoDatabase("mongodb://localhost:27017", "devops_metrics")

# Insert pod
db.upsert_pod(
    pod_id="123",
    pod_name="My App",
    stack="Java",
    business_unit="Engineering",
    tier="1"
)

# Insert metrics
metrics = {
    'pod_id': '123',
    'week_date': '2026-04-07',
    'dpi': 85.5,
    'Release_Velocity_Score': 90.0,
    'apis_published_iadp': True,
    'apis_published_apix': False,
    # ... other metrics
}
db.insert_weekly_metrics(metrics)

# Query latest metrics
df = db.get_latest_metrics()
print(df)

# Close connection
db.close()
```

---

## 📦 Backup and Restore

### Backup to JSON

```python
from src.data.mongodb import MongoDatabase

db = MongoDatabase("mongodb://localhost:27017", "devops_metrics")
backup_files = db.backup_to_json("backups")
print(f"Backup saved: {backup_files}")
```

### Restore from mongodump

```bash
# Backup
mongodump --uri="mongodb://localhost:27017" --db=devops_metrics --out=backup/

# Restore
mongorestore --uri="mongodb://localhost:27017" --db=devops_metrics backup/devops_metrics/
```

---

## ✅ Checklist

- [ ] Install pymongo: `pip install pymongo`
- [ ] Set `MONGODB_URI` in `.env`
- [ ] Test connection: `python -c "from src.data.mongodb import MongoDatabase; MongoDatabase()"`
- [ ] Run platform: `python main.py refresh`
- [ ] Verify data in MongoDB
- [ ] Set up backups
