#!/bin/bash
cd "$(dirname "$0")"
echo "Running QUICK test mode..."
python run_tests.py --quick --email biomarkerextract@test.com
