# DevOps Transformation Platform

A comprehensive gamification platform for tracking and improving DevOps maturity across teams. This platform collects DORA metrics, calculates Git hygiene scores, computes pillar scores, and generates automated repository documentation using LLM.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Database Setup](#database-setup)
  - [Weekly Refresh](#weekly-refresh)
  - [Dashboard](#dashboard)
  - [Testing](#testing)
- [Registry Configuration](#registry-configuration)
- [Documentation Generation](#documentation-generation)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

---

## Features

### 📊 Metrics Collection
- **DORA Metrics**: Release Frequency (RF), Lead Time to Deploy (LTTD), Mean Time to Recover (MTTR), Change Failure Rate (CFR)
- **Git Hygiene Scores**: Stale branches, large PRs, unreviewed PRs
- **Pillar Scores**: Speed, Quality, Stability, Automation
- **DPI (DevOps Performance Index)**: Overall team performance score

### 🎮 Gamification
- **Badge System**: Bronze, Silver, Gold, Platinum badges for achievements
- **Leaderboards**: Team rankings and performance tracking
- **Historical Trends**: Week-over-week progress visualization

### 📄 Automated Documentation
- **LLM-Powered Analysis**: Automatic repository documentation generation
- **Evidence-Based**: Uses README, package.json, Dockerfile, and other key files
- **Structured Output**: Markdown documentation with architecture, tech stack, and workflows

### 🎨 Interactive Dashboard
- **Streamlit UI**: Modern, responsive web interface
- **Real-time Filtering**: By app, team, tier, stack
- **Visualizations**: Charts, graphs, and trend analysis

---

## Architecture

```
Gamification/
├── src/
│   ├── api/              # External API clients
│   │   ├── datasight.py  # DataSight DORA metrics API
│   │   ├── github.py     # GitHub API (hygiene scores)
│   │   └── llm.py        # LLM Gateway (doc generation)
│   ├── core/             # Business logic
│   │   ├── calculator.py # Metrics calculations
│   │   └── badges.py     # Badge computation
│   ├── data/             # Data layer
│   │   ├── database.py   # SQLite database
│   │   └── registry.py   # App registry loader
│   └── utils/            # Utilities
│       └── config.py     # Configuration management
├── apps/                 # App registry YAML files
├── tests/                # Test suite
├── docs/                 # Documentation
│   └── generated/        # Auto-generated repo docs
├── main.py               # Main entry point
├── app.py                # Streamlit dashboard
└── metrics.db            # SQLite database
```

---

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Git**: Version control

### Required API Access
- **DataSight API**: For DORA metrics
- **GitHub API**: For repository hygiene checks
- **LLM Gateway**: For documentation generation (optional)

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Gamification
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python main.py --help
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required for metrics collection
DATASIGHT_BEARER_TOKEN=your_datasight_token_here

# Required for Git hygiene checks
GITHUB_TOKEN=your_github_token_here

# Optional: For documentation generation
AM_TOKEN=your_llm_api_token_here

# Optional: Enable doc generation during refresh
ENABLE_DOCS_GENERATION=true
```

### Configuration File

The platform uses `src/utils/config.py` for configuration management. Default settings:

- **Database**: `metrics.db`
- **Registry Directory**: `apps/`
- **Log Level**: `INFO`

---

## Usage

### Quick Start

1. **Setup database**:
   ```bash
   python main.py setup
   ```

2. **Load data** (run weekly refresh):
   ```bash
   python main.py refresh
   ```

3. **Launch dashboard**:
   ```bash
   streamlit run app.py
   ```

### Database Setup

Initialize the database before first use:

```bash
python main.py setup
```

**Output:**
```
✅ Database setup complete!
   Path: metrics.db
   Total pods: 0
   Total metrics records: 0
```

### Weekly Refresh

Collect metrics and calculate scores (this loads data into the database):

```bash
# Basic refresh (metrics + hygiene)
python main.py refresh

# With verbose logging
python main.py refresh -v

# With documentation generation
ENABLE_DOCS_GENERATION=true python main.py refresh
```

**What happens during refresh:**

1. **Metrics Collection Phase**
   - Fetches DORA metrics from DataSight API
   - Calculates Git hygiene scores from GitHub
   - Computes pillar scores and DPI
   - Saves to database

2. **Documentation Generation Phase** (if enabled)
   - Analyzes each repository
   - Generates markdown documentation
   - Saves to `docs/generated/<app_name>/`

**Sample Output:**
```
============================================================
Starting Weekly Data Refresh
============================================================
GitHub hygiene checking ENABLED
LLM documentation generation ENABLED
Loaded 15 applications from registry

Processing: GCDU (9594666)
  Checking hygiene for 3 repositories
    GCDU-Repository/repo-1: score=85
  ✓ DPI: 78.5 | Badges: 2

============================================================
Metrics Collection Complete
============================================================
  Processed: 15
  Failed: 0
  Average DPI: 75.2

============================================================
Starting Documentation Generation
============================================================
[DOC-GEN] Processing app: GCDU (3 repos)
[DOC-GEN] --- Repo: GCDU-Repository/repo-1 ---
[DOC-GEN] Found 45 files in repository
[DOC-GEN] Collected 5 evidence files
[DOC-GEN] LLM analysis complete!
[DOC-GEN] ✓ Documentation saved to: docs/generated/GCDU/repo-1.md

✅ Weekly refresh complete!
   Processed: 15 applications
   Average DPI: 75.2

📄 Documentation generation:
   Generated: 45
   Failed: 0
   Output: docs/generated/
```

### Dashboard

Launch the interactive Streamlit dashboard:

```bash
streamlit run app.py
```

**Access at:** http://localhost:8501

**Features:**
- Filter by app, team, tier, stack
- View current scores and badges
- Analyze historical trends
- Compare team performance

### Testing

#### Run Full Test Suite

```bash
python main.py test
```

#### Run Specific Tests

```bash
# Test database operations
pytest tests/test_database.py -v

# Test registry loading
pytest tests/test_registry.py -v

# Test metrics calculations
pytest tests/test_calculator.py -v
```

#### Database Testing Utility

Use the database test script for manual testing:

```bash
# Populate with sample data
python tests/test_database.py populate

# Inspect current data
python tests/test_database.py inspect

# Show database schema
python tests/test_database.py schema

# Clear all data
python tests/test_database.py clear
```

---

## Registry Configuration

Apps are configured via YAML files in the `apps/` directory.

### Sample Registry File: `apps/9594666.yaml`

```yaml
app_id: 9594666
app_name: GCDU
business_unit: Global Banking
tier: Tier 1
stack: Java

# TeamBook configuration
teambook_pods:
  - GCDU-Pod-1
  - GCDU-Pod-2
teambook_level: "5"

# Repository configuration (supports multiple formats)
repos:
  - git_org: GCDU-Repository
    repo_name: gdt-mds-gcdu-101-acct-srch-pa
  - git_org: GCDU-Repository
    repos:
      - https://alm-github.systems.uk.hsbc/GCDU-Repository/repo-1
      - https://alm-github.systems.uk.hsbc/GCDU-Repository/repo-2

# DevOps configuration flags
ci_automated: true
cd_automated: true
monitoring: true
logging: true
security_scanning: true
code_coverage: true
```

### Registry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_id` | string | Yes | Unique application identifier |
| `app_name` | string | Yes | Application display name |
| `business_unit` | string | Yes | Business unit/department |
| `tier` | string | Yes | Application tier (1-4) |
| `stack` | string | Yes | Technology stack |
| `teambook_pods` | array | Yes | TeamBook pod names for metrics |
| `teambook_level` | string | Yes | TeamBook hierarchy level |
| `repos` | array | Yes | Repository configurations |
| `ci_automated` | boolean | No | CI/CD automation flag |
| `cd_automated` | boolean | No | Continuous deployment flag |
| `monitoring` | boolean | No | Monitoring enabled |
| `logging` | boolean | No | Logging enabled |
| `security_scanning` | boolean | No | Security scanning enabled |
| `code_coverage` | boolean | No | Code coverage tracking |

---

## Documentation Generation

### Enable Documentation Generation

```bash
# Option 1: Environment variable
ENABLE_DOCS_GENERATION=true python main.py refresh

# Option 2: Add to .env file
echo "ENABLE_DOCS_GENERATION=true" >> .env
python main.py refresh
```

### How It Works

1. **Evidence Collection**: Fetches key files from GitHub
   - README.md, README.rst
   - package.json, pom.xml, build.gradle
   - Dockerfile, docker-compose.yml
   - .github/workflows/*.yml

2. **LLM Analysis**: Sends evidence to LLM for analysis
   - Identifies key components
   - Extracts tech stack
   - Documents interfaces and workflows

3. **Documentation Generation**: Creates structured markdown
   - Overview and summary
   - Architecture and components
   - Tech stack
   - Interfaces and APIs
   - Workflows
   - Configuration

### Output Location

```
docs/generated/
├── GCDU/
│   ├── GCDU-Repository_repo-1.md
│   └── GCDU-Repository_repo-2.md
├── AnotherApp/
│   └── AnotherOrg_another-repo.md
```

### Sample Generated Documentation

```markdown
# Repository Documentation

**Repository**: `GCDU-Repository/repo-1`
**Generated**: 2026-04-06 12:30:00

## Overview

Spring Boot microservice for account search functionality...

## Architecture

### Key Components
- REST API controller for account queries
- Service layer with business logic
- JPA repositories for data access

## Tech Stack
- Java 17
- Spring Boot 3.0
- PostgreSQL
- Docker

## Interfaces & APIs
- GET /api/v1/accounts - Search accounts
- POST /api/v1/accounts - Create account

## Workflows
- CI/CD via GitHub Actions
- Automated testing on PR
- Docker image build and push
```

---

## Troubleshooting

### Common Issues

#### 1. Database Errors

**Problem**: `sqlite3.OperationalError: no such table`

**Solution**:
```bash
python main.py setup
```

#### 2. Missing Environment Variables

**Problem**: `DATASIGHT_BEARER_TOKEN not configured`

**Solution**: Create `.env` file with required tokens
```bash
echo "DATASIGHT_BEARER_TOKEN=your_token" >> .env
echo "GITHUB_TOKEN=your_token" >> .env
```

#### 3. GitHub API Rate Limiting

**Problem**: `GitHub API error 403`

**Solution**: 
- Check token validity
- Wait for rate limit reset
- Use authenticated requests (token required)

#### 4. Stale Branch Issues

**Problem**: All branches showing as stale

**Solution**: Check logs with verbose mode
```bash
python main.py refresh -v
```

Look for:
- `[HYGIENE] ACTIVE branch` vs `[HYGIENE] STALE branch`
- API errors or authentication issues
- Date parsing errors

#### 5. LLM Documentation Fails

**Problem**: `AM_TOKEN environment variable not set`

**Solution**:
```bash
echo "AM_TOKEN=your_llm_token" >> .env
```

### Debug Mode

Enable verbose logging for detailed diagnostics:

```bash
python main.py refresh -v
```

**Log Prefixes:**
- `[HYGIENE]` - Git hygiene calculations
- `[DOC-GEN]` - Documentation generation
- `[API]` - External API calls

---

## Development

### Project Structure

```
src/
├── api/              # External integrations
├── core/             # Business logic
├── data/             # Data access layer
└── utils/            # Shared utilities
```

### Adding New Metrics

1. **Update DataSight Client** (`src/api/datasight.py`)
2. **Add to Calculator** (`src/core/calculator.py`)
3. **Update Database Schema** (`src/data/database.py`)
4. **Update Dashboard** (`app.py`)

### Adding New Badges

Edit `src/core/badges.py`:

```python
def compute_badges(self, scores: Dict[str, float]) -> List[str]:
    badges = []
    
    # Add new badge logic
    if scores.get('new_metric', 0) > 90:
        badges.append('new_badge')
    
    return badges
```

### Code Style

- **PEP 8**: Python style guide
- **Type Hints**: Use for function signatures
- **Docstrings**: Required for all public functions
- **Logging**: Use module-level logger

### Running Tests Locally

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run with coverage
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

---

## API Reference

### Main Commands

```bash
# Initialize database
python main.py setup

# Run weekly refresh (loads data into database)
python main.py refresh

# Launch dashboard
streamlit run app.py

# Run tests
python main.py test
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATASIGHT_BEARER_TOKEN` | Yes | DataSight API authentication |
| `GITHUB_TOKEN` | Yes | GitHub API authentication |
| `AM_TOKEN` | No | LLM Gateway authentication |
| `ENABLE_DOCS_GENERATION` | No | Enable doc generation (true/false) |

---

## Support

### Logs Location

Logs are written to stdout. Redirect to file if needed:

```bash
python main.py refresh > refresh.log 2>&1
```

### Database Inspection

```bash
# SQLite CLI
sqlite3 metrics.db

# View tables
.tables

# Query data
SELECT * FROM pods;
SELECT * FROM weekly_metrics ORDER BY week_date DESC LIMIT 10;
```

### Contact

For issues or questions, contact the DevOps Transformation Team.

---

## License

Internal use only - HSBC DevOps Transformation Platform

---

## Changelog

### v1.0.0 (2026-04-06)
- Initial release
- DORA metrics collection
- Git hygiene scoring
- Badge system
- Streamlit dashboard
- LLM-powered documentation generation
- Enterprise GitHub support
- Improved stale branch detection
