#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${YELLOW}=== Running $1 ===${NC}\n"
}

# Function to run a check and handle its status
run_check() {
    local name=$1
    local command=$2
    
    print_header "$name"
    if eval "$command"; then
        echo -e "${GREEN}✓ $name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $name failed${NC}"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -a, --all        Run all checks"
    echo "  -f, --format     Run formatting checks (black, isort)"
    echo "  -l, --lint       Run linting checks (flake8, pylint)"
    echo "  -t, --type       Run type checking (mypy)"
    echo "  -s, --security   Run security checks (bandit, safety)"
    echo "  -d, --docs       Run documentation checks (pydocstyle)"
    echo "  -c, --complexity Run complexity checks (vulture, radon)"
    echo "  -h, --help       Show this help message"
}

# Check if pipenv is available
if ! command -v pipenv &> /dev/null; then
    echo -e "${RED}Error: pipenv is not installed${NC}"
    exit 1
fi

# If no arguments provided, show usage
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            RUN_ALL=true
            shift
            ;;
        -f|--format)
            RUN_FORMAT=true
            shift
            ;;
        -l|--lint)
            RUN_LINT=true
            shift
            ;;
        -t|--type)
            RUN_TYPE=true
            shift
            ;;
        -s|--security)
            RUN_SECURITY=true
            shift
            ;;
        -d|--docs)
            RUN_DOCS=true
            shift
            ;;
        -c|--complexity)
            RUN_COMPLEXITY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Run all checks if --all is specified
if [ "$RUN_ALL" = true ]; then
    RUN_FORMAT=true
    RUN_LINT=true
    RUN_TYPE=true
    RUN_SECURITY=true
    RUN_DOCS=true
    RUN_COMPLEXITY=true
fi

# Initialize error counter
ERRORS=0

# Formatting checks
if [ "$RUN_FORMAT" = true ]; then
    run_check "Black" "pipenv run black . --check" || ((ERRORS++))
    run_check "isort" "pipenv run isort . --check-only" || ((ERRORS++))
fi

# Linting checks
if [ "$RUN_LINT" = true ]; then
    run_check "Flake8" "pipenv run flake8 ." || ((ERRORS++))
    run_check "Pylint" "pipenv run pylint ." || ((ERRORS++))
fi

# Type checking
if [ "$RUN_TYPE" = true ]; then
    run_check "Mypy" "pipenv run mypy ." || ((ERRORS++))
fi

# Security checks
if [ "$RUN_SECURITY" = true ]; then
    run_check "Bandit" "pipenv run bandit -r ." || ((ERRORS++))
    run_check "Safety" "pipenv run safety check" || ((ERRORS++))
fi

# Documentation checks
if [ "$RUN_DOCS" = true ]; then
    run_check "Pydocstyle" "pipenv run pydocstyle ." || ((ERRORS++))
fi

# Complexity checks
if [ "$RUN_COMPLEXITY" = true ]; then
    run_check "Vulture" "pipenv run vulture . --min-confidence=80" || ((ERRORS++))
    run_check "Radon" "pipenv run radon cc . --min=A" || ((ERRORS++))
fi

# Print summary
echo -e "\n${YELLOW}=== Summary ===${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}$ERRORS check(s) failed${NC}"
    exit 1
fi 