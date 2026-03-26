# Pipeline Maturity Skill (20% weight)

## Purpose
Analyze CI/CD pipeline maturity and automation capabilities to provide recommendations for improvement.

## Analysis Criteria

### 1. CI/CD Automation Level
- **Check for**: Automated build, test, deploy pipelines
- **Look for**: CI/CD tools, automation coverage
- **Good indicators**:
  - Fully automated CI/CD pipeline
  - Automated testing at multiple levels
  - Zero-touch deployments

### 2. Testing Automation
- **Check for**: Unit, integration, E2E test automation
- **Look for**: Test coverage, automated test execution
- **Good indicators**:
  - High test coverage (>80%)
  - Automated test execution on every PR
  - Fast feedback loops (<10 min)

### 3. Deployment Automation
- **Check for**: Deployment automation, rollback capabilities
- **Look for**: Infrastructure as Code, automated provisioning
- **Good indicators**:
  - One-click deployments
  - Automated rollback on failure
  - Infrastructure as Code (Terraform, CloudFormation)

## YAML Fields to Analyze

```yaml
# Key fields that indicate pipeline maturity:
- ci_cd_pipeline: (presence and type)
- automation_tools: (Jenkins, GitHub Actions, GitLab CI, etc.)
- testing_framework: (if present)
- deployment_automation: (if present)
- infrastructure_as_code: (if present)
```

## Recommendation Template

```
### Pipeline Maturity Recommendations for [APP_NAME]

**Current State Analysis:**
- CI/CD Status: [Present/Absent/Partial]
- [Other observations from YAML]

**Gaps Identified:**
1. [Gap 1 - e.g., No automated testing mentioned]
2. [Gap 2 - e.g., Manual deployment process]

**Recommended Actions:**
1. **Implement Automated CI/CD Pipeline** (Priority: High)
   - Description: Set up end-to-end automated pipeline
   - Expected Impact: Faster deployments, reduced errors
   - Implementation:
     - Choose CI/CD tool (GitHub Actions recommended)
     - Create pipeline configuration (.github/workflows)
     - Automate build, test, deploy stages
     - Add deployment gates and approvals

2. **Add Automated Testing** (Priority: High)
   - Description: Implement comprehensive test automation
   - Expected Impact: Catch bugs early, improve quality
   - Implementation:
     - Set up unit test framework
     - Add integration tests
     - Configure automated test execution in CI
     - Set minimum coverage threshold (80%)

3. **Enable Automated Rollback** (Priority: Medium)
   - Description: Implement automatic rollback on deployment failure
   - Expected Impact: Faster recovery, reduced downtime
   - Implementation:
     - Add health checks post-deployment
     - Configure automatic rollback triggers
     - Test rollback procedures regularly

**Estimated Score Impact:** +X points (current: Y → target: Z)
```

## Scoring Guidelines

- **85-100**: Elite - Full automation, IaC, automated rollback, comprehensive testing
- **70-84**: High - Mostly automated, good testing, some manual steps
- **50-69**: Medium - Partial automation, basic testing, manual deployments
- **Below 50**: Low - Minimal automation, manual processes

## Red Flags to Watch For

- No CI/CD pipeline mentioned
- Manual build/test/deploy processes
- No testing automation
- No rollback capability
- No infrastructure as code
- Long deployment times
