# YAML Schema Migration Guide

## New Fields Required (Updated Calculator Logic)

Your mentor updated the calculator logic. You need to add these fields to **ALL** your app YAML files.

---

## 📋 New Fields to Add

### 1. Compliance Section
Add this field to the `# ── COMPLIANCE ──` section:

```yaml
repo_docs: ""  # URL or path to repository documentation
```

**Scoring Impact**: 20 points in Compliance pillar

---

### 2. AI & Adoption Section
**REPLACE** the old adoption fields with these new ones:

**OLD (Remove these):**
```yaml
ai_tools_declared: []  # OLD: was an array
apis_published: false  # OLD: single boolean
api_count: 0          # OLD: single count
```

**NEW (Add these):**
```yaml
ai_tools_declared: false  # NEW: Boolean - true if AI tools are declared/tracked
ai_devops_onboarded: false  # NEW: Boolean - true if team completed AI DevOps onboarding
apis_published_iadp: 0  # NEW: Number of APIs published in IADP (max 2 for full score)
apis_published_apix: 0  # NEW: Number of APIs published in APIX (max 2 for full score)
```

**Scoring Impact**:
- `ai_tools_declared`: 10 points (was 25 points)
- `ai_devops_onboarded`: 20 points (NEW)
- `apis_published_iadp`: 10 points per API, max 20 points (NEW)
- `apis_published_apix`: 10 points per API, max 20 points (NEW)

---

## 📝 Complete Updated YAML Template

Here's the complete updated section for your YAML files:

```yaml
# ── COMPLIANCE ────────────────────────────────────────────
release_page_url: ""
compliance_evidence_page: ""
repo_docs: ""  # URL or path to repository documentation

# ── AI & ADOPTION ─────────────────────────────────────────
copilot_enabled: false
ai_tools_declared: false  # Boolean: true if AI tools are declared/tracked
ai_devops_onboarded: false  # Boolean: true if team completed AI DevOps onboarding
ai_test_generation: false
apis_published_iadp: 0  # Number of APIs published in IADP (max 2 for full score)
apis_published_apix: 0  # Number of APIs published in APIX (max 2 for full score)
catalog_url: ""
feature_flags_adopted: false  # Currently not used in scoring
```

---

## 🔄 What Changed in Scoring

### Compliance Pillar (5 components @ 20 points each = 100 max)
- ✅ Release page URL: 20 points
- ✅ Compliance evidence page: 20 points
- ✅ **Repo docs: 20 points** ← NEW
- ✅ Privileged access current: 20 points
- ✅ CR auto-creation: 20 points

### Adoption Pillar (100 max)
- ✅ Copilot enabled: 30 points
- ✅ AI tools declared: 10 points (was 25)
- ✅ **APIs published (IADP)**: up to 20 points ← NEW (1 API = 10 pts, max 2)
- ✅ **APIs published (APIX)**: up to 20 points ← NEW (1 API = 10 pts, max 2)
- ✅ **AI DevOps onboarded**: 20 points ← NEW
- ❌ Feature flags: 0 points (removed from scoring)

---

## ✅ What You Need to Do

1. **Update ALL app YAML files** in `/apps/` directory
2. Add the 4 new fields to each file:
   - `repo_docs`
   - `ai_devops_onboarded`
   - `apis_published_iadp`
   - `apis_published_apix`
3. Change `ai_tools_declared` from array `[]` to boolean `false`
4. Remove old `apis_published` and `api_count` fields (optional, backward compatible)

---

## 🚀 Files Already Updated

- ✅ `/apps/GCDU_EXAMPLE.yaml` - Updated with new schema
- ✅ `/src/data/registry.py` - Updated to parse new fields
- ✅ `/src/core/calculator.py` - Updated with new scoring logic

---

## 📊 Example Migration

**Before:**
```yaml
# ── COMPLIANCE ────────────────────────────────────────────
release_page_url: ""
compliance_evidence_page: ""

# ── AI & ADOPTION ─────────────────────────────────────────
copilot_enabled: false
ai_tools_declared: []
apis_published: false
api_count: 0
```

**After:**
```yaml
# ── COMPLIANCE ────────────────────────────────────────────
release_page_url: ""
compliance_evidence_page: ""
repo_docs: ""  # NEW

# ── AI & ADOPTION ─────────────────────────────────────────
copilot_enabled: false
ai_tools_declared: false  # Changed from array to boolean
ai_devops_onboarded: false  # NEW
apis_published_iadp: 0  # NEW
apis_published_apix: 0  # NEW
```

---

## 🔍 Backward Compatibility

The system is **backward compatible**:
- Old YAML files will still work (fields default to 0/false)
- Old `apis_published` field is still parsed but not used in scoring
- You can update files gradually

However, **teams won't get full scores** until you add the new fields!

---

## 📞 Questions?

If you have questions about:
- What values to use for existing teams
- How to track IADP vs APIX APIs
- AI DevOps onboarding status

Ask your mentor or check with the teams directly.
