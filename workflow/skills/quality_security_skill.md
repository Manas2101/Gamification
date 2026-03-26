# Quality & Security Skill (10% weight)

## Purpose
Analyze application security and quality practices to identify vulnerabilities and improvement opportunities.

## Analysis Criteria

### 1. Security Scanning
- **Check for**: SAST, DAST, dependency scanning
- **Look for**: Security tools integration, vulnerability management
- **Good indicators**:
  - Automated SAST/DAST in CI/CD
  - Regular dependency vulnerability scans
  - Security gates in deployment pipeline

### 2. Code Quality Practices
- **Check for**: Code quality tools, static analysis
- **Look for**: Linting, code coverage, quality gates
- **Good indicators**:
  - Automated code quality checks
  - Minimum code coverage requirements
  - Quality gates preventing bad code merges

### 3. Privileged Access Management
- **Check for**: Privileged access requirements
- **Look for**: Secrets management, least privilege
- **Good indicators**:
  - No privileged access needed for deployments
  - Secrets stored in vault/secrets manager
  - Service accounts with minimal permissions

## YAML Fields to Analyze

```yaml
# Key fields that indicate quality & security:
- security_scanning: (SAST, DAST tools)
- code_quality_tools: (SonarQube, CodeClimate, etc.)
- secrets_management: (Vault, AWS Secrets Manager, etc.)
- privileged_access_required: (yes/no)
- vulnerability_scanning: (if present)
```

## Recommendation Template

```
### Quality & Security Recommendations for [APP_NAME]

**Current State Analysis:**
- Security Scanning: [Present/Absent]
- [Other observations from YAML]

**Gaps Identified:**
1. [Gap 1 - e.g., No SAST/DAST scanning]
2. [Gap 2 - e.g., Privileged access required]

**Recommended Actions:**
1. **Implement Automated Security Scanning** (Priority: High)
   - Description: Add SAST and DAST to CI/CD pipeline
   - Expected Impact: Early vulnerability detection, reduced security risks
   - Implementation:
     - Integrate SAST tool (e.g., SonarQube, Snyk)
     - Add DAST scanning for runtime vulnerabilities
     - Configure security gates in pipeline
     - Set up vulnerability tracking and remediation

2. **Eliminate Privileged Access Requirements** (Priority: High)
   - Description: Redesign deployment to use service accounts
   - Expected Impact: Reduced security risk, better compliance
   - Implementation:
     - Create service accounts with minimal permissions
     - Implement secrets management (HashiCorp Vault)
     - Remove hard-coded credentials
     - Use IAM roles for cloud deployments

3. **Add Code Quality Gates** (Priority: Medium)
   - Description: Enforce code quality standards
   - Expected Impact: Better code maintainability, fewer bugs
   - Implementation:
     - Set up SonarQube or similar tool
     - Define quality gates (coverage >80%, no critical issues)
     - Add pre-commit hooks for linting
     - Create code quality dashboard

**Estimated Score Impact:** +X points (current: Y → target: Z)
```

## Scoring Guidelines

- **85-100**: Elite - Full security automation, no privileged access, comprehensive quality checks
- **70-84**: High - Good security practices, minimal privileged access, quality gates
- **50-69**: Medium - Basic security scanning, some privileged access, basic quality checks
- **Below 50**: Low - Minimal security, high privileged access, no quality automation

## Red Flags to Watch For

- No security scanning mentioned
- Privileged access required for deployments
- Hard-coded credentials
- No code quality tools
- No vulnerability management
- Manual security reviews only
