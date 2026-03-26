# Release Velocity Skill (30% weight)

## Purpose
Analyze application configuration to assess release velocity capabilities and provide recommendations for improvement.

## Analysis Criteria

### 1. Deployment Frequency
- **Check for**: CI/CD pipeline configuration
- **Look for**: Automated deployment triggers, deployment frequency indicators
- **Good indicators**: 
  - Multiple deployments per day/week
  - Automated deployment on merge to main
  - Feature flags for gradual rollouts

### 2. Lead Time for Changes
- **Check for**: Development workflow indicators
- **Look for**: Branch strategies, PR merge frequency
- **Good indicators**:
  - Short-lived feature branches
  - Fast PR review cycles
  - Automated testing before merge

### 3. Release Process Maturity
- **Check for**: Release documentation, rollback capabilities
- **Look for**: Deployment automation level
- **Good indicators**:
  - Zero-touch deployments
  - Automated rollback mechanisms
  - Blue-green or canary deployments

## YAML Fields to Analyze

```yaml
# Key fields that indicate velocity:
- repos: (number of repos, complexity)
- deployment_frequency: (if present)
- ci_cd_tools: (Jenkins, GitHub Actions, etc.)
- release_strategy: (continuous, scheduled, manual)
```

## Recommendation Template

When analyzing, provide recommendations in this format:

```
### Release Velocity Recommendations for [APP_NAME]

**Current State Analysis:**
- [What you observed in the YAML]

**Gaps Identified:**
1. [Gap 1]
2. [Gap 2]

**Recommended Actions:**
1. **[Action Title]** (Priority: High/Medium/Low)
   - Description: [What to do]
   - Expected Impact: [How this improves velocity]
   - Implementation: [Specific steps]

2. **[Action Title]** (Priority: High/Medium/Low)
   - Description: [What to do]
   - Expected Impact: [How this improves velocity]
   - Implementation: [Specific steps]

**Estimated Score Impact:** +X points (current: Y → target: Z)
```

## Scoring Guidelines

- **85-100**: Elite - Multiple daily deployments, full automation, instant rollback
- **70-84**: High - Daily/weekly deployments, mostly automated, good rollback
- **50-69**: Medium - Weekly/bi-weekly deployments, some automation
- **Below 50**: Low - Monthly or manual deployments, minimal automation

## Red Flags to Watch For

- Manual deployment processes
- No CI/CD pipeline mentioned
- Long release cycles (monthly or longer)
- No rollback strategy
- Single repository with no deployment info
