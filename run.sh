#!/bin/bash
# Run script for DevOps Transformation Platform

set -e

echo "🚀 DevOps Transformation Platform - Run Script"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one from .env.example"
    echo "   cp .env.example .env"
    echo "   Then edit .env with your API tokens"
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-help}

case $COMMAND in
    setup)
        echo "📦 Setting up database..."
        python setup_database.py
        echo "✅ Database setup complete!"
        ;;
    
    refresh)
        echo "🔄 Running weekly data refresh..."
        python weekly_refresh.py
        echo "✅ Data refresh complete!"
        ;;
    
    dashboard)
        echo "📊 Launching dashboard..."
        streamlit run app.py
        ;;
    
    test)
        echo "🧪 Running tests..."
        pytest tests/ -v
        ;;
    
    test-cov)
        echo "🧪 Running tests with coverage..."
        pytest tests/ --cov=. --cov-report=html --cov-report=term
        echo "📊 Coverage report generated in htmlcov/index.html"
        ;;
    
    lint)
        echo "🔍 Running linter..."
        flake8 . --exclude=venv,__pycache__,.git --max-line-length=120
        ;;
    
    format)
        echo "✨ Formatting code..."
        black . --exclude='venv|__pycache__|\.git'
        ;;
    
    clean)
        echo "🧹 Cleaning up..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete
        find . -type f -name "*.pyo" -delete
        find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
        echo "✅ Cleanup complete!"
        ;;
    
    install)
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        echo "✅ Installation complete!"
        ;;
    
    help|*)
        echo ""
        echo "Usage: ./run.sh [command]"
        echo ""
        echo "Available commands:"
        echo "  setup       - Initialize database"
        echo "  refresh     - Run weekly data refresh"
        echo "  dashboard   - Launch Streamlit dashboard"
        echo "  test        - Run test suite"
        echo "  test-cov    - Run tests with coverage report"
        echo "  lint        - Run code linter"
        echo "  format      - Format code with black"
        echo "  clean       - Clean up temporary files"
        echo "  install     - Install dependencies"
        echo "  help        - Show this help message"
        echo ""
        ;;
esac
