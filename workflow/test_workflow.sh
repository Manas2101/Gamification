#!/bin/bash

# Quick test script for the agentic workflow
# This creates a test scenario and runs the workflow

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

echo "🧪 Testing Agentic Recommendation Workflow"
echo "=========================================="
echo ""

# Step 1: Create a test change
echo "Step 1: Creating test change..."
cp workflow/example_app.yaml apps/test_payment_app.yaml
git add apps/test_payment_app.yaml
echo "✓ Created test app: apps/test_payment_app.yaml"
echo ""

# Step 2: Run detection
echo "Step 2: Testing change detection..."
python3 workflow/detect_app_changes.py
echo ""

# Step 3: Run analysis
echo "Step 3: Testing app analysis..."
python3 workflow/analyze_app.py apps/test_payment_app.yaml
echo ""

# Step 4: Generate prompt
echo "Step 4: Testing prompt generation..."
python3 workflow/generate_prompt.py apps/test_payment_app.yaml
echo ""

# Step 5: Show results
echo "Step 5: Checking generated files..."
echo ""
echo "Generated files:"
ls -lh workflow/recommendations/ 2>/dev/null || echo "No recommendations directory yet"
echo ""

# Step 6: Run full workflow
echo "Step 6: Running full workflow..."
python3 workflow/run_workflow.py
echo ""

echo "=========================================="
echo "✅ Test complete!"
echo ""
echo "Next steps:"
echo "1. Check workflow/recommendations/ for generated files"
echo "2. Review the prompt in workflow/recommendations/test_payment_app_prompt.txt"
echo "3. Run: ./workflow/automate_windsurf.sh workflow/recommendations/test_payment_app_prompt.txt test_payment_app"
echo "4. Or manually paste the prompt into Windsurf chat"
echo ""
echo "To clean up test files:"
echo "  git reset HEAD apps/test_payment_app.yaml"
echo "  rm apps/test_payment_app.yaml"
echo "  rm -rf workflow/recommendations/"
