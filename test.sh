#!/bin/bash
# Quick test runner for Antarctic Mystery Validator

echo "🧊 Antarctic Mystery Validator - Test Runner"
echo "=============================================="
echo ""

cd "$(dirname "$0")/mystery_validator" || exit 1

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Run the validator
echo "Running validator..."
echo ""

python3 main.py

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ All validations passed!"
else
    echo "⚠️  Some validations failed (see details above)"
fi

exit $exit_code
