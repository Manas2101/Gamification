"""
Test Git Hygiene Scoring for GCDU App
======================================

This test demonstrates the complete hygiene score calculation for the GCDU app,
showing how violations are detected and how they impact the final score.

The hygiene checker evaluates repositories across multiple categories:
1. Stale Branches (max deduction: 35 points)
2. PR Issues (max deduction: 40 points)
3. Branch Protection (max deduction: 25 points)

Each violation has a severity (critical/warning) and a point deduction.
The final score is calculated as: 100 - total_deductions (capped by category limits)

Author: DevOps Transformation Team
"""

import pytest
from datetime import datetime, timezone, timedelta
from src.core.hygiene_checker import (
    HygieneChecker,
    RepoHygieneResult,
    Violation,
    SCORE_BASE,
    CHECK_SCORING,
    CATEGORY_CAPS
)


class MockGitHubClient:
    """Mock GitHub client for testing without actual API calls."""
    
    def __init__(self, mock_data):
        """
        Initialize mock client with test data.
        
        Args:
            mock_data: Dictionary containing mock responses for branches, PRs, etc.
        """
        self.mock_data = mock_data
    
    def get_branches(self, repo_full_name, api_base=None):
        """Return mock branches data."""
        return self.mock_data.get('branches', [])
    
    def get_open_pull_requests(self, repo_full_name, api_base=None):
        """Return mock PRs data."""
        return self.mock_data.get('prs', [])
    
    def _make_request(self, url, api_base=None):
        """Mock API request handler."""
        # Handle commit requests
        if '/commits/' in url:
            commit_sha = url.split('/commits/')[-1]
            commits = self.mock_data.get('commits', {})
            if commit_sha in commits:
                return 200, commits[commit_sha]
            return 404, {}
        
        # Handle PR reviews
        if '/reviews' in url:
            pr_num = url.split('/pulls/')[-1].split('/')[0]
            reviews = self.mock_data.get('reviews', {})
            return 200, reviews.get(pr_num, [])
        
        # Handle branch protection
        if '/protection' in url:
            branch = url.split('/branches/')[-1].split('/')[0]
            protection = self.mock_data.get('protection', {})
            if branch in protection:
                return 200, protection[branch]
            return 404, {"message": "Branch not protected"}
        
        # Handle events
        if '/events' in url:
            return 200, self.mock_data.get('events', [])
        
        return 404, {}


class TestGCDUHygieneScoring:
    """Test suite for GCDU hygiene scoring calculations."""
    
    def test_perfect_score_no_violations(self):
        """
        Test Case 1: Perfect Repository (Score: 100)
        
        Scenario:
        - No stale branches
        - No open PRs
        - Branch protection enabled
        - No direct pushes
        
        Expected Result: Score = 100
        """
        mock_data = {
            'branches': [
                {
                    'name': 'main',
                    'commit': {'sha': 'abc123'}
                }
            ],
            'commits': {
                'abc123': {
                    'commit': {
                        'committer': {
                            'date': datetime.now(timezone.utc).isoformat()
                        }
                    }
                }
            },
            'prs': [],
            'protection': {
                'main': {
                    'required_status_checks': {'strict': True},
                    'enforce_admins': {'enabled': True}
                }
            },
            'events': []
        }
        
        config = {
            'max_branch_age_days': 30,
            'max_pr_lines_changed': 400,
            'max_pr_review_hours': 24,
            'protected_branches': ['main', 'master']
        }
        
        gh_client = MockGitHubClient(mock_data)
        checker = HygieneChecker(gh_client, config)
        
        result = checker.check_repo('GCDU-Repository', 'gdt-mds-gcdu-101-acct-srch-pa')
        
        assert result.score == 100, f"Expected perfect score 100, got {result.score}"
        assert len(result.violations) == 0, f"Expected no violations, got {len(result.violations)}"
        assert result.passed is True
        
        print("\n✅ Test Case 1: Perfect Score")
        print(f"   Score: {result.score}/100")
        print(f"   Violations: {len(result.violations)}")
    
    def test_stale_branches_deduction(self):
        """
        Test Case 2: Stale Branches (Score: ~65-93)
        
        Scenario:
        - 2 stale branches (warning severity): 2 × 2 = 4 points
        - 1 very stale branch (critical severity): 1 × 5 = 5 points
        - Total raw deduction: 9 points
        - Category cap: 35 points (not reached)
        
        Expected Result: Score = 100 - 9 = 91
        """
        now = datetime.now(timezone.utc)
        
        mock_data = {
            'branches': [
                {
                    'name': 'main',
                    'commit': {'sha': 'main123'}
                },
                {
                    'name': 'feature/old-feature-1',
                    'commit': {'sha': 'old1'}
                },
                {
                    'name': 'feature/old-feature-2',
                    'commit': {'sha': 'old2'}
                },
                {
                    'name': 'feature/very-old',
                    'commit': {'sha': 'veryold'}
                }
            ],
            'commits': {
                'main123': {
                    'commit': {
                        'committer': {
                            'date': now.isoformat()
                        }
                    }
                },
                'old1': {
                    'commit': {
                        'committer': {
                            'date': (now - timedelta(days=45)).isoformat()
                        }
                    }
                },
                'old2': {
                    'commit': {
                        'committer': {
                            'date': (now - timedelta(days=50)).isoformat()
                        }
                    }
                },
                'veryold': {
                    'commit': {
                        'committer': {
                            'date': (now - timedelta(days=120)).isoformat()
                        }
                    }
                }
            },
            'prs': [],
            'protection': {'main': {'required_status_checks': {}}},
            'events': []
        }
        
        config = {
            'max_branch_age_days': 30,
            'max_pr_lines_changed': 400,
            'max_pr_review_hours': 24,
            'protected_branches': ['main', 'master']
        }
        
        gh_client = MockGitHubClient(mock_data)
        checker = HygieneChecker(gh_client, config)
        
        result = checker.check_repo('GCDU-Repository', 'gdt-mds-gcdu-101-acct-srch-pa')
        
        breakdown = result.score_breakdown()
        
        print("\n✅ Test Case 2: Stale Branches")
        print(f"   Score: {result.score}/100")
        print(f"   Violations: {len(result.violations)}")
        print(f"   Breakdown:")
        print(f"     - Base Score: {breakdown['base_score']}")
        print(f"     - Total Deduction: {breakdown['total_deduction']}")
        print(f"     - Final Score: {breakdown['final_score']}")
        
        for check_name, check_data in breakdown['checks'].items():
            print(f"     - {check_name}: {check_data['count']} violations, "
                  f"{check_data['applied_deduction']} points deducted")
        
        assert result.score == 91, f"Expected score 91, got {result.score}"
        assert len(result.violations) == 3
    
    def test_oversized_pr_deduction(self):
        """
        Test Case 3: Oversized PRs (Score: ~76-88)
        
        Scenario:
        - 1 oversized PR (critical): 12 points
        - Category cap: 40 points for PRs (not reached)
        
        Expected Result: Score = 100 - 12 = 88
        """
        now = datetime.now(timezone.utc)
        
        mock_data = {
            'branches': [{'name': 'main', 'commit': {'sha': 'main123'}}],
            'commits': {
                'main123': {
                    'commit': {
                        'committer': {'date': now.isoformat()}
                    }
                }
            },
            'prs': [
                {
                    'number': 42,
                    'title': 'feat: Add massive feature',
                    'html_url': 'https://github.com/GCDU/repo/pull/42',
                    'user': {'login': 'developer1'},
                    'created_at': (now - timedelta(hours=2)).isoformat(),
                    'additions': 600,
                    'deletions': 200
                }
            ],
            'reviews': {
                '42': [
                    {'state': 'APPROVED'}
                ]
            },
            'protection': {'main': {'required_status_checks': {}}},
            'events': []
        }
        
        config = {
            'max_branch_age_days': 30,
            'max_pr_lines_changed': 400,
            'max_pr_review_hours': 24,
            'protected_branches': ['main', 'master']
        }
        
        gh_client = MockGitHubClient(mock_data)
        checker = HygieneChecker(gh_client, config)
        
        result = checker.check_repo('GCDU-Repository', 'gdt-mds-gcdu-101-acct-srch-pa')
        
        breakdown = result.score_breakdown()
        
        print("\n✅ Test Case 3: Oversized PR")
        print(f"   Score: {result.score}/100")
        print(f"   Violations: {len(result.violations)}")
        print(f"   PR Size: 800 lines (limit: 400)")
        print(f"   Deduction: {breakdown['total_deduction']} points")
        
        assert result.score == 88, f"Expected score 88, got {result.score}"
        assert result.critical_count == 1
    
    def test_unreviewed_pr_deduction(self):
        """
        Test Case 4: Unreviewed PRs (Score: ~88-94)
        
        Scenario:
        - 1 PR open for 30 hours without review (warning): 6 points
        
        Expected Result: Score = 100 - 6 = 94
        """
        now = datetime.now(timezone.utc)
        
        mock_data = {
            'branches': [{'name': 'main', 'commit': {'sha': 'main123'}}],
            'commits': {
                'main123': {
                    'commit': {
                        'committer': {'date': now.isoformat()}
                    }
                }
            },
            'prs': [
                {
                    'number': 15,
                    'title': 'fix: Bug fix waiting for review',
                    'html_url': 'https://github.com/GCDU/repo/pull/15',
                    'user': {'login': 'developer2'},
                    'created_at': (now - timedelta(hours=30)).isoformat(),
                    'additions': 50,
                    'deletions': 20
                }
            ],
            'reviews': {
                '15': []  # No reviews
            },
            'protection': {'main': {'required_status_checks': {}}},
            'events': []
        }
        
        config = {
            'max_branch_age_days': 30,
            'max_pr_lines_changed': 400,
            'max_pr_review_hours': 24,
            'protected_branches': ['main', 'master']
        }
        
        gh_client = MockGitHubClient(mock_data)
        checker = HygieneChecker(gh_client, config)
        
        result = checker.check_repo('GCDU-Repository', 'gdt-mds-gcdu-101-acct-srch-pa')
        
        print("\n✅ Test Case 4: Unreviewed PR")
        print(f"   Score: {result.score}/100")
        print(f"   Violations: {len(result.violations)}")
        print(f"   PR Age: 30 hours (SLA: 24 hours)")
        
        assert result.score == 94, f"Expected score 94, got {result.score}"
        assert result.warning_count == 1
    
    def test_missing_branch_protection(self):
        """
        Test Case 5: Missing Branch Protection (Score: 75)
        
        Scenario:
        - Main branch has no protection rules (critical): 25 points
        - Category cap: 25 points (reached)
        
        Expected Result: Score = 100 - 25 = 75
        """
        now = datetime.now(timezone.utc)
        
        mock_data = {
            'branches': [{'name': 'main', 'commit': {'sha': 'main123'}}],
            'commits': {
                'main123': {
                    'commit': {
                        'committer': {'date': now.isoformat()}
                    }
                }
            },
            'prs': [],
            'protection': {},  # No protection rules
            'events': []
        }
        
        config = {
            'max_branch_age_days': 30,
            'max_pr_lines_changed': 400,
            'max_pr_review_hours': 24,
            'protected_branches': ['main', 'master']
        }
        
        gh_client = MockGitHubClient(mock_data)
        checker = HygieneChecker(gh_client, config)
        
        result = checker.check_repo('GCDU-Repository', 'gdt-mds-gcdu-101-acct-srch-pa')
        
        print("\n✅ Test Case 5: Missing Branch Protection")
        print(f"   Score: {result.score}/100")
        print(f"   Violations: {len(result.violations)}")
        print(f"   Critical Issues: {result.critical_count}")
        
        assert result.score == 75, f"Expected score 75, got {result.score}"
        assert result.passed is False  # Critical violation
    
    def test_gcdu_realistic_scenario(self):
        """
        Test Case 6: GCDU Realistic Scenario (Score: ~50-65)
        
        This simulates a real GCDU repository with multiple issues:
        - 5 stale branches (3 warning + 2 critical)
        - 2 oversized PRs
        - 1 unreviewed PR
        - Missing branch protection
        - 1 direct push to main
        
        Calculation:
        1. Stale Branches:
           - 3 warning × 2 = 6 points
           - 2 critical × 5 = 10 points
           - Raw: 16 points, Capped at 35 → 16 points
        
        2. PR Issues:
           - 2 oversized (critical) × 12 = 24 points
           - 1 unreviewed (warning) × 6 = 6 points
           - Raw: 30 points, Capped at 40 → 30 points
        
        3. Protection Issues:
           - 1 missing protection × 25 = 25 points
           - 1 direct push × 25 = 50 points raw
           - Raw: 50 points, Capped at 25 → 25 points
        
        Total Deduction: 16 + 30 + 25 = 71 points
        Expected Score: 100 - 71 = 29
        """
        now = datetime.now(timezone.utc)
        
        mock_data = {
            'branches': [
                {'name': 'main', 'commit': {'sha': 'main123'}},
                {'name': 'feature/stale-1', 'commit': {'sha': 'stale1'}},
                {'name': 'feature/stale-2', 'commit': {'sha': 'stale2'}},
                {'name': 'feature/stale-3', 'commit': {'sha': 'stale3'}},
                {'name': 'feature/very-stale-1', 'commit': {'sha': 'vstale1'}},
                {'name': 'feature/very-stale-2', 'commit': {'sha': 'vstale2'}},
            ],
            'commits': {
                'main123': {'commit': {'committer': {'date': now.isoformat()}}},
                'stale1': {'commit': {'committer': {'date': (now - timedelta(days=40)).isoformat()}}},
                'stale2': {'commit': {'committer': {'date': (now - timedelta(days=45)).isoformat()}}},
                'stale3': {'commit': {'committer': {'date': (now - timedelta(days=50)).isoformat()}}},
                'vstale1': {'commit': {'committer': {'date': (now - timedelta(days=100)).isoformat()}}},
                'vstale2': {'commit': {'committer': {'date': (now - timedelta(days=120)).isoformat()}}},
            },
            'prs': [
                {
                    'number': 101,
                    'title': 'feat: Large refactoring',
                    'html_url': 'https://github.com/GCDU/repo/pull/101',
                    'user': {'login': 'dev1'},
                    'created_at': (now - timedelta(hours=5)).isoformat(),
                    'additions': 700,
                    'deletions': 300
                },
                {
                    'number': 102,
                    'title': 'feat: Another big change',
                    'html_url': 'https://github.com/GCDU/repo/pull/102',
                    'user': {'login': 'dev2'},
                    'created_at': (now - timedelta(hours=3)).isoformat(),
                    'additions': 500,
                    'deletions': 400
                },
                {
                    'number': 103,
                    'title': 'fix: Small fix needing review',
                    'html_url': 'https://github.com/GCDU/repo/pull/103',
                    'user': {'login': 'dev3'},
                    'created_at': (now - timedelta(hours=30)).isoformat(),
                    'additions': 20,
                    'deletions': 10
                }
            ],
            'reviews': {
                '101': [{'state': 'APPROVED'}],
                '102': [{'state': 'APPROVED'}],
                '103': []
            },
            'protection': {},  # No protection
            'events': [
                {
                    'type': 'PushEvent',
                    'created_at': (now - timedelta(days=2)).isoformat(),
                    'payload': {
                        'ref': 'refs/heads/main',
                        'commits': [{'sha': 'abc123'}]
                    },
                    'actor': {'login': 'admin'}
                }
            ]
        }
        
        config = {
            'max_branch_age_days': 30,
            'max_pr_lines_changed': 400,
            'max_pr_review_hours': 24,
            'protected_branches': ['main', 'master'],
            'allow_direct_push_to_main': False
        }
        
        gh_client = MockGitHubClient(mock_data)
        checker = HygieneChecker(gh_client, config)
        
        result = checker.check_repo('GCDU-Repository', 'gdt-mds-gcdu-101-acct-srch-pa')
        
        breakdown = result.score_breakdown()
        
        print("\n✅ Test Case 6: GCDU Realistic Scenario")
        print(f"   Final Score: {result.score}/100")
        print(f"   Total Violations: {len(result.violations)}")
        print(f"   Critical: {result.critical_count}, Warning: {result.warning_count}")
        print(f"\n   Score Breakdown:")
        print(f"     Base Score: {breakdown['base_score']}")
        print(f"     Total Deduction: {breakdown['total_deduction']}")
        print(f"\n   By Category:")
        for category, data in breakdown['categories'].items():
            print(f"     {category}: -{data['applied_deduction']} points (cap: {data['cap']})")
        print(f"\n   By Check Type:")
        for check, data in breakdown['checks'].items():
            print(f"     {check}: {data['count']} violations, -{data['applied_deduction']} points")
        
        assert result.score == 29, f"Expected score 29, got {result.score}"
        assert result.passed is False
        assert len(result.violations) == 10  # 5 stale + 2 oversized + 1 unreviewed + 1 protection + 1 direct push


if __name__ == '__main__':
    """Run tests and display detailed scoring breakdown."""
    print("=" * 80)
    print("GCDU Git Hygiene Scoring Test Suite")
    print("=" * 80)
    
    test_suite = TestGCDUHygieneScoring()
    
    # Run all tests
    test_suite.test_perfect_score_no_violations()
    test_suite.test_stale_branches_deduction()
    test_suite.test_oversized_pr_deduction()
    test_suite.test_unreviewed_pr_deduction()
    test_suite.test_missing_branch_protection()
    test_suite.test_gcdu_realistic_scenario()
    
    print("\n" + "=" * 80)
    print("SCORING REFERENCE")
    print("=" * 80)
    print("\nCategory Caps:")
    for category, cap in CATEGORY_CAPS.items():
        print(f"  {category}: {cap} points max deduction")
    
    print("\nCheck Scoring Rules:")
    for check, rules in CHECK_SCORING.items():
        print(f"\n  {check}:")
        print(f"    Category: {rules['category']}")
        print(f"    Max Deduction: {rules['max_deduction']}")
        print(f"    Severity Weights: {rules['severity_weights']}")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)
