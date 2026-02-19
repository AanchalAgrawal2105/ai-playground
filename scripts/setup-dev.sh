#!/bin/bash

# Development environment setup script
# Usage: ./scripts/setup-dev.sh

set -e

echo "🔧 Setting up development environment for Airflow Monitoring..."

# Check if Python is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Python version (require 3.8+)
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8+ is required, but found Python $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install package in development mode with all extras
echo "📥 Installing package and dependencies..."
pip install -e ".[dev,test]"

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Create environment file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env file with your actual configuration values"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs config tests/fixtures

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
pytest tests/ -v --maxfail=1

# Start development services
echo "🐳 Starting development services with Docker..."
docker-compose -f docker-compose.dev.yml up -d postgres postgres-test

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Run a quick integration test
echo "🔍 Testing database connectivity..."
python -c "
import os
from sqlalchemy import create_engine, text
try:
    engine = create_engine('postgresql://airflow_test:airflow_test@localhost:5433/airflow_test')
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✅ Test database connection successful')
except Exception as e:
    print(f'⚠️  Test database connection failed: {e}')
    print('This is normal if you haven\'t configured the test database yet')
"

echo "✅ Development environment setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run tests: pytest"
echo "4. Start development: python -m src.airflow_monitoring.airflow_runtime_agent"
echo "5. Access services:"
echo "   - Main DB: postgresql://localhost:5432/airflow"
echo "   - Test DB: postgresql://localhost:5433/airflow_test"