#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PYTHON_TESTS_PASSED=false
JS_TESTS_PASSED=false

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

check_python() {
    print_info "Checking Python installation"
    if command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version)
        print_success "Python found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python not found."
        return 1
    fi
}

check_node() {
    print_info "Checking Node.js installation"
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
        return 0
    else
        print_error "Node.js not found."
        return 1
    fi
}

install_python_deps() {
    print_info "Installing Python test dependencies"

    if [ -f "requirements-test.txt" ]; then
        pip3 install -r requirements-test.txt -q
        print_success "Python dependencies installed"
    else
        print_info "No requirements-test.txt found"
    fi
}

# Install Node.js dependencies
install_node_deps() {
    print_info "Installing Node.js test dependencies"

    if [ -f "package.json" ]; then
        npm install --silent
        print_success "Node.js dependencies installed"
    else
        print_error "package.json not found"
        return 1
    fi
}

# Run Python unit tests
run_python_tests() {

    if [ -d "backend/tests" ]; then
        print_info "Running Python tests"

        if python -m pytest backend/tests/ -v --tb=short; then
            print_success "All Python tests passed!"
            PYTHON_TESTS_PASSED=true
        else
            print_error "Some Python tests failed"
            PYTHON_TESTS_PASSED=false
        fi
    else
        print_error "backend/tests directory not found"
        PYTHON_TESTS_PASSED=false
    fi
}

run_js_tests() {

    if [ -f "tests/test.spec.js" ]; then
        print_info "Running Playwright tests"

        if npm test; then
            print_success "All JavaScript tests passed!"
            JS_TESTS_PASSED=true
        else
            print_error "Some JavaScript tests failed"
            JS_TESTS_PASSED=false
        fi
    else
        print_error "tests/test.spec.js not found"
        JS_TESTS_PASSED=false
    fi
}

# Run linting
run_linting() {
    print_info "Running Python linting (flake8)"
    if command -v flake8 &> /dev/null; then
        flake8 backend/ --max-line-length=120 --ignore=E501,W503 || true
        print_success "Python linting complete"
    else
        print_info "flake8 not installed"
    fi
}

# Print summary
print_summary() {

    if [ "$PYTHON_TESTS_PASSED" = true ]; then
        print_success "Python Tests: PASSED"
    else
        print_error "Python Tests: FAILED"
    fi

    if [ "$JS_TESTS_PASSED" = true ]; then
        print_success "JavaScript Tests: PASSED"
    else
        print_error "JavaScript Tests: FAILED"
    fi

    echo ""

    if [ "$PYTHON_TESTS_PASSED" = true ] && [ "$JS_TESTS_PASSED" = true ]; then
        print_success "All tests passed!"
        return 0
    else
        print_error "Some tests failed. Please review the output above."
        return 1
    fi
}

main() {
    check_python || exit 1
    check_node || exit 1

    install_python_deps
    install_node_deps

    case "${1:-all}" in
        python)
            run_python_tests
            ;;
        js|javascript)
            run_js_tests
            ;;
        lint)
            run_linting
            ;;
        all)
            run_python_tests
            run_js_tests
            run_linting
            ;;
        *)
            echo "Usage: $0 {all|python|js|lint|coverage}"
            echo ""
            echo "Options:"
            echo "  all       - Run all tests (default)"
            echo "  python    - Run only Python tests"
            echo "  js        - Run only JavaScript tests"
            echo "  lint      - Run code linting"
            exit 1
            ;;
    esac

    print_summary
}

main "$@"