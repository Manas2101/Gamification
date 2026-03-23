# How to Fix Git Hygiene Scoring - Fill in Repos in YAML

## Problem
Git Hygiene is always returning 100 because the `repos` section in your YAML files is empty.

## Example: Current (WRONG) ❌
```yaml
repos:
  - git_org: ""                 # EMPTY!
    repo_name: ""               # EMPTY!
    role: "backend"
    is_primary: true
```

## Example: Correct (RIGHT) ✅
```yaml
repos:
  - git_org: "hsbc-enterprise"           # Your GitHub organization
    repo_name: "rdh-backend-service"     # Your repository name
    role: "backend"
    is_primary: true

  - git_org: "hsbc-enterprise"
    repo_name: "rdh-frontend"
    role: "frontend"
    is_primary: false
```

## Real-World Example
If your GitHub repo URL is: `https://github.com/hsbc-enterprise/payment-api`

Then fill in:
```yaml
repos:
  - git_org: "hsbc-enterprise"
    repo_name: "payment-api"
    role: "backend"
    is_primary: true
```

## What Gets Checked
Once you fill in the repos, the system will automatically check:

1. **Stale Branches** (deduct 5 points each)
   - Branches not updated in 30+ days
   - Excludes main/master branches

2. **Large PRs** (deduct 10 points each)
   - PRs with >500 lines changed
   - Critical violation

3. **Unreviewed PRs** (deduct 5 points each)
   - PRs open >24 hours with no reviews
   - Warning violation

## How to Fill Your YAML Files

### Step 1: Find your repos
Go to your team's GitHub organization and list all repos for your app.

### Step 2: Update each YAML file
For each app in `apps/*.yaml`:

1. Open the file
2. Find the `repos:` section (around line 55)
3. Fill in `git_org` and `repo_name` for each repo
4. Mark ONE repo as `is_primary: true` (the main backend repo)
5. Save the file

### Step 3: Run weekly refresh
```bash
python weekly_refresh.py
```

You'll now see logs like:
```
INFO: Checking Git hygiene for RDH repo: hsbc-enterprise/rdh-backend-service
INFO:   Found stale branch 'feature/old-work' (last commit: 2024-01-15)
INFO:   Found large PR #123 (850 lines changed)
INFO:   Final Git Hygiene score for RDH: 75.0/100 (critical: 1, warnings: 1)
```

## GitHub Token Setup

Make sure your `.env` file has:
```bash
GITHUB_TOKEN=ghp_your_actual_github_token_here
```

Get a token from: https://github.com/settings/tokens
- Required scopes: `repo` (full control of private repositories)

## Quick Fix Checklist

- [ ] Fill in `git_org` and `repo_name` in all YAML files
- [ ] Mark one repo as `is_primary: true` per app
- [ ] Verify `GITHUB_TOKEN` is set in `.env`
- [ ] Run `python weekly_refresh.py`
- [ ] Check logs for "Checking Git hygiene for..." messages
- [ ] Run `python debug_database.py` to see actual scores
