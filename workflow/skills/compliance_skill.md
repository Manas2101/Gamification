# Compliance Skill (15% weight)

## Purpose
Analyze compliance and governance practices to ensure applications meet regulatory and organizational standards.

## Analysis Criteria

### 1. Release Documentation
- **Check for**: Release notes, change logs, documentation
- **Look for**: Documentation standards, release evidence
- **Good indicators**:
  - Automated release notes generation
  - Comprehensive change documentation
  - Audit trail for all releases

### 2. Access Control & Reviews
- **Check for**: Access management, periodic reviews
- **Look for**: Role-based access, access audit logs
- **Good indicators**:
  - Regular access reviews (quarterly)
  - Principle of least privilege
  - Automated access provisioning/deprovisioning

### 3. Compliance Artifacts
- **Check for**: Compliance evidence, audit logs
- **Look for**: Regulatory compliance indicators
- **Good indicators**:
  - Automated compliance checks
  - Evidence collection for audits
  - Compliance dashboards

## YAML Fields to Analyze

```yaml
# Key fields that indicate compliance:
- compliance_framework: (SOX, GDPR, HIPAA, etc.)
- documentation_required: (if present)
- access_control: (if present)
- audit_logging: (if present)
- release_approval_process: (if present)
```

## Recommendation Template

```
### Compliance Recommendations for [APP_NAME]

**Current State Analysis:**
- Compliance Framework: [Identified/Not specified]
- [Other observations from YAML]

**Gaps Identified:**
1. [Gap 1 - e.g., No release documentation process]
2. [Gap 2 - e.g., No access review process mentioned]

**Recommended Actions:**
1. **Implement Automated Release Documentation** (Priority: High)
   - Description: Auto-generate release notes from commits/PRs
   - Expected Impact: Better audit trail, compliance readiness
   - Implementation:
     - Set up release notes automation tool
     - Create release documentation template
     - Link releases to tickets/issues
     - Store release artifacts securely

2. **Establish Access Review Process** (Priority: High)
   - Description: Quarterly access reviews and certifications
   - Expected Impact: Reduced security risk, compliance adherence
   - Implementation:
     - Document current access levels
     - Schedule quarterly access reviews
     - Implement automated access reporting
     - Create access request/approval workflow

3. **Enable Audit Logging** (Priority: Medium)
   - Description: Comprehensive logging of all changes
   - Expected Impact: Better traceability, audit readiness
   - Implementation:
     - Enable application audit logs
     - Set up centralized log collection
     - Define log retention policies
     - Create audit log dashboards

**Estimated Score Impact:** +X points (current: Y → target: Z)
```

## Scoring Guidelines

- **85-100**: Elite - Full compliance automation, comprehensive documentation, regular audits
- **70-84**: High - Good documentation, regular reviews, most compliance automated
- **50-69**: Medium - Basic documentation, some manual compliance processes
- **Below 50**: Low - Minimal documentation, manual compliance, no regular reviews

## Red Flags to Watch For

- No release documentation process
- No access control mentioned
- No audit logging
- No compliance framework specified
- Manual compliance processes
- No evidence collection for audits
