# Git Hygiene Skill (20% weight)

## Purpose
Analyze repository hygiene practices and provide recommendations for maintaining clean, healthy codebases.

## Analysis Criteria

### 1. Branch Management
- **Check for**: Stale branches, branch naming conventions
- **Look for**: Branch cleanup policies, protected branches
- **Good indicators**:
  - Automated stale branch deletion
  - Clear branch naming strategy
  - Protected main/production branches

### 2. Pull Request Practices
- **Check for**: PR size, review requirements
- **Look for**: PR templates, review policies
- **Good indicators**:
  - Small, focused PRs (< 400 lines)
  - Required reviews before merge
  - PR templates for consistency

### 3. Code Review Culture
- **Check for**: Review turnaround time
- **Look for**: Review automation, approval requirements
- **Good indicators**:
  - Reviews completed within 24-48 hours
  - At least 1-2 reviewers required
  - Automated code quality checks

## YAML Fields to Analyze

```yaml
# Key fields that indicate hygiene:
- repos: (number and structure)
- git_org: (organization structure)
- branch_protection: (if present)
- review_requirements: (if present)
```

## Recommendation Template

```
### Git Hygiene Recommendations for [APP_NAME]

**Current State Analysis:**
- Repository count: [X repos]
- [Other observations from YAML]

**Gaps Identified:**
1. [Gap 1 - e.g., No branch protection mentioned]
2. [Gap 2 - e.g., Multiple repos may have stale branches]

**Recommended Actions:**
1. **Implement Branch Cleanup Policy** (Priority: High)
   - Description: Set up automated deletion of branches merged >30 days ago
   - Expected Impact: Reduces clutter, improves repo navigation
   - Implementation: 
     - Enable GitHub branch protection rules
     - Set up automated branch cleanup workflow
     - Document branch naming conventions

2. **Enforce PR Size Limits** (Priority: Medium)
   - Description: Encourage smaller, focused PRs
   - Expected Impact: Faster reviews, better code quality
   - Implementation:
     - Add PR size checker in CI
     - Create PR template with size guidelines
     - Team training on effective PR practices

**Estimated Score Impact:** +X points (current: Y → target: Z)
```

## Scoring Guidelines

- **85-100**: Elite - No stale branches, small PRs, fast reviews, full automation
- **70-84**: High - Minimal stale branches, good PR practices, timely reviews
- **50-69**: Medium - Some stale branches, variable PR sizes, slower reviews
- **Below 50**: Low - Many stale branches, large PRs, slow/no reviews

## Red Flags to Watch For

- No mention of code review process
- Large number of repositories without hygiene policies
- No branch protection
- No PR templates or guidelines
- Manual merge processes
