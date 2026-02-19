#!/bin/bash

# Run tests script with different test types
# Usage: ./scripts/run-tests.sh [unit|integration|e2e|all]

set -e

TEST_TYPE=${1:-all}

echo "🧪 Running tests: $TEST_TYPE"

# Activate virtual environment if it exists
if [[ -d "venv" ]]; then
    source venv/bin/activate
fi

# Function to run specific test types
run_tests() {
    local test_marker=$1
    local description=$2
    
    echo "📋 Running $description tests..."
    
    if [[ "$test_marker" == "all" ]]; then
        pytest tests/ -v \
            --cov=src/airflow_monitoring \
            --cov-report=term-missing \
            --cov-report=html:htmlcov \
            --cov-report=xml \
            --junitxml=test-results.xml
    else
        pytest tests/ -v \
            -m "$test_marker" \
            --cov=src/airflow_monitoring \
            --cov-report=term-missing
    fi
}

# Run tests based on type
case $TEST_TYPE in
    "unit")
        run_tests "unit" "unit"
        ;;
    "integration") 
        # Start test services
        echo "🐳 Starting test services..."
        docker-compose -f docker-compose.dev.yml up -d postgres-test
        sleep 5
        
        run_tests "integration" "integration"
        
        # Clean up
        docker-compose -f docker-compose.dev.yml down
        ;;
    "e2e")
        echo "🌐 Starting full test environment..."
        docker-compose -f docker-compose.dev.yml up -d
        sleep 15
        
        run_tests "e2e" "end-to-end"
        
        # Clean up
        docker-compose -f docker-compose.dev.yml down
        ;;
    "all")
        echo "🚀 Running all tests..."
        
        # Start all test services
        docker-compose -f docker-compose.dev.yml up -d
        sleep 15
        
        run_tests "all" "all"
        
        # Clean up
        docker-compose -f docker-compose.dev.yml down
        ;;
    *)
        echo "❌ Unknown test type: $TEST_TYPE"
        echo "Valid options: unit, integration, e2e, all"
        exit 1
        ;;
esac

echo "✅ Tests completed!"

# Show coverage report location
if [[ -f "htmlcov/index.html" ]]; then
    echo "📊 Coverage report available at: htmlcov/index.html"
fi