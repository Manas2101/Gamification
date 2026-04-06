"""
Git Hygiene Checker
===================

Comprehensive hygiene checker that runs all Git hygiene checks against repos.

Checks performed:
  1. Stale branches (age > max_branch_age_days)
  2. Oversized PRs (lines changed > max_pr_lines_changed)
  3. Unreviewed PRs (open > max_pr_review_hours without a review)
  4. PR titles not matching the required pattern
  5. Direct pushes to main/master (branch protection bypass)
  6. Missing branch protection rules

Author: DevOps Transformation Team
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


CHECK_FRIENDLY = {
    "api_error": "API Check Error",
    "stale_branch": "Stale Branch",
    "pr_size": "Oversized PR",
    "pr_review_sla": "Unreviewed PR",
    "pr_title_format": "PR Title Format",
    "direct_push_to_main": "Direct Push to Main",
    "branch_protection": "Missing Branch Protection",
}

SCORE_BASE = 100
DEFAULT_SEVERITY_WEIGHTS = {
    "critical": 10,
    "warning": 5,
    "info": 2,
}

CHECK_SCORING = {
    "stale_branch": {
        "category": "branches",
        "severity_weights": {"warning": 2, "critical": 5},
        "max_deduction": 35,
    },
    "pr_size": {
        "category": "prs",
        "severity_weights": {"critical": 12},
        "max_deduction": 24,
    },
    "pr_review_sla": {
        "category": "prs",
        "severity_weights": {"warning": 6, "critical": 12},
        "max_deduction": 24,
    },
    "pr_title_format": {
        "category": "prs",
        "severity_weights": {"warning": 2},
        "max_deduction": 10,
    },
    "branch_protection": {
        "category": "protection",
        "severity_weights": {"critical": 25},
        "max_deduction": 25,
    },
    "direct_push_to_main": {
        "category": "protection",
        "severity_weights": {"critical": 25},
        "max_deduction": 25,
    },
}

CATEGORY_CAPS = {
    "branches": 35,
    "prs": 40,
    "protection": 25,
}


@dataclass
class Violation:
    """Represents a single hygiene violation."""
    repo: str
    check: str
    severity: str
    title: str
    detail: str
    url: str = ""
    metadata: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "repo": self.repo,
            "check": self.check,
            "severity": self.severity,
            "title": self.title,
            "detail": self.detail,
            "url": self.url,
            "metadata": self.metadata,
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }


@dataclass
class RepoHygieneResult:
    """Results of hygiene checks for a single repository."""
    repo_full_name: str
    violations: List[Violation] = field(default_factory=list)
    score: Optional[int] = SCORE_BASE
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: str = ""

    def add(self, v: Violation):
        """Add a violation and recalculate score."""
        self.violations.append(v)
        if v.check == "api_error":
            self.score = None
            return
        if self.score is None:
            return
        self.score = self._calculate_score()

    def _calculate_score(self) -> int:
        """Calculate hygiene score based on violations."""
        return max(0, SCORE_BASE - self.score_breakdown()["total_deduction"])

    def score_breakdown(self) -> dict:
        """Calculate detailed score breakdown by category and check."""
        check_totals: Dict[str, dict] = {}
        category_totals: Dict[str, dict] = {}

        for violation in self.violations:
            if violation.check == "api_error":
                continue

            scoring_rule = CHECK_SCORING.get(violation.check, {})
            category = scoring_rule.get("category", "other")
            severity_weights = scoring_rule.get("severity_weights", DEFAULT_SEVERITY_WEIGHTS)
            weight = severity_weights.get(
                violation.severity,
                DEFAULT_SEVERITY_WEIGHTS.get(violation.severity, 5),
            )

            check_entry = check_totals.setdefault(
                violation.check,
                {
                    "category": category,
                    "count": 0,
                    "raw_deduction": 0,
                    "max_deduction": scoring_rule.get("max_deduction"),
                },
            )
            check_entry["count"] += 1
            check_entry["raw_deduction"] += weight

        for check_name, check_entry in check_totals.items():
            raw_deduction = check_entry["raw_deduction"]
            max_deduction = check_entry["max_deduction"]
            applied_deduction = min(raw_deduction, max_deduction) if max_deduction is not None else raw_deduction
            check_entry["applied_deduction"] = applied_deduction

            category_name = check_entry["category"]
            category_entry = category_totals.setdefault(
                category_name,
                {
                    "raw_deduction": 0,
                    "cap": CATEGORY_CAPS.get(category_name),
                },
            )
            category_entry["raw_deduction"] += applied_deduction

        total_deduction = 0
        for category_name, category_entry in category_totals.items():
            cap = category_entry["cap"]
            raw_deduction = category_entry["raw_deduction"]
            applied_deduction = min(raw_deduction, cap) if cap is not None else raw_deduction
            category_entry["applied_deduction"] = applied_deduction
            total_deduction += applied_deduction

        return {
            "base_score": SCORE_BASE,
            "total_deduction": total_deduction,
            "final_score": max(0, SCORE_BASE - total_deduction),
            "categories": category_totals,
            "checks": check_totals,
        }

    def mark_api_error(self, detail: str, title: str = "API Check Error"):
        """Mark this result as having an API error."""
        self.error_message = detail
        error_detail = f"Could not check repo: {detail}"
        if any(v.check == "api_error" and v.detail == error_detail for v in self.violations):
            self.score = None
            return
        self.add(Violation(
            repo=self.repo_full_name,
            check="api_error",
            severity="warning",
            title=title,
            detail=error_detail,
            metadata={"error": detail},
        ))

    @property
    def passed(self) -> bool:
        """Check if repo passed (no critical violations)."""
        return not self.error_message and not any(
            v.severity == "critical"
            for v in self.violations
        )

    @property
    def critical_count(self) -> int:
        """Count of critical violations."""
        return sum(1 for v in self.violations if v.severity == "critical")

    @property
    def warning_count(self) -> int:
        """Count of warning violations."""
        return sum(1 for v in self.violations if v.severity == "warning")


class HygieneChecker:
    """
    Comprehensive hygiene checker for Git repositories.
    
    Runs all hygiene checks and returns detailed results with scoring.
    """

    def __init__(self, github_client, config: dict):
        """
        Initialize hygiene checker.
        
        Args:
            github_client: GitHubClient instance for API calls
            config: Hygiene configuration dictionary from settings.yaml
        """
        self.gh = github_client
        self.config = config

    def check_repo(self, owner: str, repo: str, full_url: str = None) -> RepoHygieneResult:
        """
        Run all hygiene checks for a single repository.
        
        Args:
            owner: Repository owner/org
            repo: Repository name
            full_url: Full URL for enterprise GitHub (e.g., https://github.enterprise.com/org/repo)
            
        Returns:
            RepoHygieneResult with score and violations
        """
        full_name = f"{owner}/{repo}"
        result = RepoHygieneResult(repo_full_name=full_name)

        # Extract API base URL from full_url if provided
        api_base = self._get_api_base(full_url) if full_url else None

        checks = (
            self._check_stale_branches,
            self._check_open_prs,
            self._check_branch_protection,
            self._check_direct_pushes,
        )
        
        for check in checks:
            try:
                check(owner, repo, result, api_base)
            except Exception as exc:
                logger.warning(f"Check failed for {full_name}: {exc}")
                result.mark_api_error(str(exc))
                break

        return result

    def _get_api_base(self, full_url: str) -> str:
        """
        Extract API base URL from full repository URL.
        
        Args:
            full_url: Full URL like https://github.enterprise.com/org/repo
            
        Returns:
            API base URL like https://github.enterprise.com/api/v3
        """
        import re
        match = re.match(r'(https?://[^/]+)', full_url)
        if match:
            host_url = match.group(1)
            # Check if it's enterprise GitHub (not github.com)
            if 'github.com' not in host_url:
                return f"{host_url}/api/v3"
        return None

    def _check_stale_branches(self, owner: str, repo: str, result: RepoHygieneResult, api_base: str = None):
        """Check for stale branches that haven't been updated recently."""
        max_age = self.config.get("max_branch_age_days", 30)
        protected = self.config.get("protected_branches", ["main", "master"])
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=max_age)

        branches = self.gh.get_branches(f"{owner}/{repo}", api_base=api_base)
        
        for branch in branches:
            name = branch.get("name", "")
            
            # Skip protected/release branches
            if any(
                name == p or (p.endswith("*") and name.startswith(p[:-1]))
                for p in protected
            ):
                continue

            try:
                commit = branch.get("commit", {})
                commit_sha = commit.get("sha")
                if not commit_sha:
                    continue
                    
                # Get commit details to find date
                commit_url = f"repos/{owner}/{repo}/commits/{commit_sha}"
                status, commit_data = self.gh._make_request(commit_url, api_base=api_base)
                
                if status != 200 or not commit_data or "commit" not in commit_data:
                    continue
                    
                date_str = commit_data["commit"]["committer"]["date"]
                last_commit_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                
            except Exception as e:
                logger.debug(f"Could not get commit date for branch {name}: {e}")
                continue

            if last_commit_date < cutoff:
                age_days = (now - last_commit_date).days
                severity = "critical" if age_days > max_age * 3 else "warning"
                result.add(Violation(
                    repo=f"{owner}/{repo}",
                    check="stale_branch",
                    severity=severity,
                    title=f"Stale branch: `{name}`",
                    detail=(
                        f"Branch '{name}' has not been updated in {age_days} days "
                        f"(limit: {max_age} days). Last commit: {last_commit_date.strftime('%Y-%m-%d')}."
                    ),
                    url=f"https://github.com/{owner}/{repo}/branches",
                    metadata={"branch": name, "age_days": age_days},
                ))

    def _check_open_prs(self, owner: str, repo: str, result: RepoHygieneResult, api_base: str = None):
        """Check open PRs for size, review SLA, and title format."""
        max_lines = self.config.get("max_pr_lines_changed", 400)
        max_review_hours = self.config.get("max_pr_review_hours", 24)
        pr_title_pattern_str = self.config.get(
            "required_pr_pattern",
            r"^(feat|fix|chore|docs|refactor|test|ci)(\(.*\))?: .{10,}"
        )
        pr_title_pattern = re.compile(pr_title_pattern_str)
        now = datetime.now(timezone.utc)

        prs = self.gh.get_open_pull_requests(f"{owner}/{repo}", api_base=api_base)
        
        for pr in prs:
            pr_num = pr.get("number")
            pr_title = pr.get("title", "")
            pr_url = pr.get("html_url", "")
            author = pr.get("user", {}).get("login", "unknown")
            created_at_str = pr.get("created_at", "")
            
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                age_hours = (now - created_at).total_seconds() / 3600
            except:
                age_hours = 0

            # PR Size check
            additions = pr.get("additions", 0)
            deletions = pr.get("deletions", 0)
            total_lines = additions + deletions
            
            if total_lines > max_lines:
                overage_pct = round((total_lines - max_lines) / max_lines * 100)
                result.add(Violation(
                    repo=f"{owner}/{repo}",
                    check="pr_size",
                    severity="critical",
                    title=f"Oversized PR #{pr_num}: {total_lines} lines changed",
                    detail=(
                        f"PR #{pr_num} '{pr_title}' by @{author} has {total_lines} lines changed "
                        f"({overage_pct}% over the {max_lines}-line limit)."
                    ),
                    url=pr_url,
                    metadata={"pr_number": pr_num, "lines_changed": total_lines, "author": author},
                ))

            # Review SLA check
            try:
                reviews_url = f"repos/{owner}/{repo}/pulls/{pr_num}/reviews"
                status, reviews = self.gh._make_request(reviews_url, api_base=api_base)
                
                has_review = False
                if status == 200 and isinstance(reviews, list):
                    has_review = any(
                        r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED")
                        for r in reviews
                    )
                
                if not has_review and age_hours > max_review_hours:
                    result.add(Violation(
                        repo=f"{owner}/{repo}",
                        check="pr_review_sla",
                        severity="warning" if age_hours < max_review_hours * 3 else "critical",
                        title=f"PR #{pr_num} unreviewed for {int(age_hours)}h",
                        detail=(
                            f"PR #{pr_num} '{pr_title}' by @{author} has been open for {int(age_hours)} hours "
                            f"without any review (SLA: {max_review_hours}h)."
                        ),
                        url=pr_url,
                        metadata={"pr_number": pr_num, "age_hours": round(age_hours, 1), "author": author},
                    ))
            except Exception as e:
                logger.debug(f"Could not check reviews for PR #{pr_num}: {e}")

            # PR Title pattern check
            if not pr_title_pattern.match(pr_title.strip()):
                result.add(Violation(
                    repo=f"{owner}/{repo}",
                    check="pr_title_format",
                    severity="warning",
                    title=f"PR #{pr_num} title does not match required pattern",
                    detail=(
                        f"PR #{pr_num} by @{author} has a non-compliant title: '{pr_title}'. "
                        f"Required format: type(scope): description (min 10 chars)."
                    ),
                    url=pr_url,
                    metadata={"pr_number": pr_num, "author": author, "title": pr_title},
                ))

    def _check_branch_protection(self, owner: str, repo: str, result: RepoHygieneResult, api_base: str = None):
        """Check if main/master branches have protection rules enabled."""
        protected = ["main", "master"]
        
        for branch_name in protected:
            try:
                # Check if branch exists
                branches = self.gh.get_branches(f"{owner}/{repo}", api_base=api_base)
                branch_exists = any(b.get("name") == branch_name for b in branches)
                
                if not branch_exists:
                    continue

                # Check protection status (404 is expected if no protection exists)
                protection_url = f"repos/{owner}/{repo}/branches/{branch_name}/protection"
                status, protection = self.gh._make_request(protection_url, api_base=api_base)
                
                # 404 means no protection rules exist - this is a critical violation
                if status == 404 or status != 200 or not protection or "message" in protection:
                    result.add(Violation(
                        repo=f"{owner}/{repo}",
                        check="branch_protection",
                        severity="critical",
                        title=f"Branch `{branch_name}` has NO protection rules",
                        detail=(
                            f"The `{branch_name}` branch in {owner}/{repo} has no branch protection enabled. "
                            f"This allows direct pushes and bypasses CI."
                        ),
                        url=f"https://github.com/{owner}/{repo}/settings/branches",
                        metadata={"branch": branch_name},
                    ))
            except Exception as e:
                logger.debug(f"Could not check branch protection for {branch_name}: {e}")

    def _check_direct_pushes(self, owner: str, repo: str, result: RepoHygieneResult, api_base: str = None):
        """Detect recent direct commits to main/master (not via PR)."""
        if self.config.get("allow_direct_push_to_main", False):
            return

        protected = ["main", "master"]
        
        try:
            events_url = f"repos/{owner}/{repo}/events"
            status, events = self.gh._make_request(events_url, api_base=api_base)
            
            if status != 200 or not isinstance(events, list):
                return
                
            cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            
            for event in events:
                if event.get("type") != "PushEvent":
                    continue
                    
                ref = event.get("payload", {}).get("ref", "")
                branch_name = ref.replace("refs/heads/", "")
                
                if branch_name not in protected:
                    continue

                created_at_str = event.get("created_at", "")
                try:
                    pushed_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                except:
                    continue
                    
                if pushed_at < cutoff:
                    continue

                actor = event.get("actor", {}).get("login", "unknown")
                commits = event.get("payload", {}).get("commits", [])

                result.add(Violation(
                    repo=f"{owner}/{repo}",
                    check="direct_push_to_main",
                    severity="critical",
                    title=f"Direct push to `{branch_name}` by @{actor}",
                    detail=(
                        f"@{actor} pushed {len(commits)} commit(s) directly to `{branch_name}` "
                        f"on {pushed_at.strftime('%Y-%m-%d %H:%M UTC')} — bypassing the PR process."
                    ),
                    url=f"https://github.com/{owner}/{repo}/commits/{branch_name}",
                    metadata={"actor": actor, "commit_count": len(commits), "pushed_at": pushed_at.isoformat()},
                ))
        except Exception as e:
            logger.debug(f"Could not check push events: {e}")
