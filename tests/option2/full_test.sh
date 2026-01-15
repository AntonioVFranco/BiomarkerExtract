#!/bin/bash
cd "$(dirname "$0")"
echo "Running FULL test mode..."
python run_tests.py --email biomarkerextract@test.com
