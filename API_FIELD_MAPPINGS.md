# API Field Mappings

## TeamBook API Response Structure

### Endpoint: `/pod?serviceline=449`

**Response Format:**
```json
{
  "child": [
    {
      "Pod ID": 1251,
      "Pod": "DevOps Platform Team"
    },
    {
      "Pod ID": 1252,
      "Pod": "Cloud Services Pod"
    }
  ]
}
```

**Field Mapping:**
- `Pod ID` → `pod_id` (internal)
- `Pod` → `pod_name` (internal)

---

## DataSight API Response Structure

### 1. MTTR Endpoint: `/incident/metric/mttr/by-group/teambook/metric`

**Response Format:**
```json
{
  "items": [
    {
      "mttr": 1.5
    }
  ]
}
```

**Field Mapping:**
- `mttr` → `mttr` (Mean Time To Restore in hours)

---

### 2. LTTD Endpoint: `/releases/metric/lttd/teambook/metric`

**Response Format:**
```json
{
  "items": [
    {
      "lttd": 8.2
    }
  ]
}
```

**Field Mapping:**
- `lttd` → `lttd` (Lead Time To Deploy in days)

---

### 3. Release Frequency Endpoint: `/releases/metric/release-frequency/teambook/metric`

**Response Format:**
```json
{
  "items": [
    {
      "releases": 150
    }
  ]
}
```

**Field Mapping:**
- `releases` → `rf` (Release Frequency count)

---

### 4. CFR Endpoint: `/releases/metric/cfr/teambook/metric`

**Response Format:**
```json
{
  "items": [
    {
      "change_failure_rate": 0.15
    }
  ]
}
```

**Field Mapping:**
- `change_failure_rate` → `cfr` (Change Failure Rate as decimal, e.g., 0.15 = 15%)

---

## Summary Table

| API | Endpoint | Response Field | Internal Field | Description |
|-----|----------|---------------|----------------|-------------|
| TeamBook | `/pod` | `Pod ID` | `pod_id` | Unique pod identifier |
| TeamBook | `/pod` | `Pod` | `pod_name` | Pod/team name |
| DataSight | `/incident/metric/mttr/...` | `mttr` | `mttr` | Mean Time To Restore (hours) |
| DataSight | `/releases/metric/lttd/...` | `lttd` | `lttd` | Lead Time To Deploy (days) |
| DataSight | `/releases/metric/release-frequency/...` | `releases` | `rf` | Release Frequency (count) |
| DataSight | `/releases/metric/cfr/...` | `change_failure_rate` | `cfr` | Change Failure Rate (0-1) |

---

## Updated Code References

### `api_integration.py` - TeamBook
```python
pods.append({
    'pod_id': pod.get('Pod ID'),      # ← Updated
    'pod_name': pod.get('Pod')        # ← Updated
})
```

### `api_integration.py` - DataSight
```python
# MTTR - unchanged
return data['items'][0].get('mttr')

# LTTD - unchanged  
return data['items'][0].get('lttd')

# Release Frequency - UPDATED
return data['items'][0].get('releases')  # was 'releaseFrequency'

# CFR - UPDATED
return data['items'][0].get('change_failure_rate')  # was 'cfr'
```

---

## Testing

After these changes, test with:

```bash
# Fetch data with correct field mappings
python weekly_refresh.py
```

Expected log output:
```
Fetched 10 pods from TeamBook
Fetching metrics for pod: DevOps Platform Team (ID: 1251)
Stored metrics for pod: DevOps Platform Team (DPI: 85)
```

The pod names and metrics should now correctly map from the API responses! ✅
