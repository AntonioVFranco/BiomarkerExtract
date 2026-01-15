#!/bin/bash

# BiomarkerExtract Option 2: Testing & Refinement Installation

set -e

echo "======================================================================"
echo "BiomarkerExtract - Option 2: Testing & Refinement Installation"
echo "======================================================================"
echo ""

cd /mnt/c/Users/tommo/Documents/Bioinformatics/1102/BiomarkerExtract
source venv/bin/activate

echo "Step 1: Creating test directories..."
mkdir -p tests/option2
mkdir -p test_results
echo "✓ Directories created"
echo ""

echo "Step 2: Moving test suite files..."
if [ -f "validation_dataset.py" ]; then
    cp validation_dataset.py tests/option2/
    echo "✓ validation_dataset.py moved"
fi

if [ -f "test_biomarker_categories.py" ]; then
    cp test_biomarker_categories.py tests/option2/
    echo "✓ test_biomarker_categories.py moved"
fi

if [ -f "benchmark_suite.py" ]; then
    cp benchmark_suite.py tests/option2/
    echo "✓ benchmark_suite.py moved"
fi

if [ -f "accuracy_metrics.py" ]; then
    cp accuracy_metrics.py tests/option2/
    echo "✓ accuracy_metrics.py moved"
fi

if [ -f "run_tests.py" ]; then
    cp run_tests.py tests/option2/
    chmod +x tests/option2/run_tests.py
    echo "✓ run_tests.py moved and made executable"
fi

if [ -f "Option2_Testing_README.md" ]; then
    cp Option2_Testing_README.md tests/option2/README.md
    echo "✓ README.md moved"
fi
echo ""

echo "Step 3: Verifying file placement..."
echo "Test suite files:"
ls -lh tests/option2/*.py 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""

echo "Step 4: Testing validation dataset..."
cd tests/option2
python << 'PYTHON_TEST'
try:
    import validation_dataset
    dataset = validation_dataset.ValidationDataset()
    stats = dataset.get_statistics()
    print(f"✓ Validation dataset loaded: {stats['total_biomarkers']} biomarkers")
except Exception as e:
    print(f"✗ Error: {e}")
PYTHON_TEST
cd ../..
echo ""

echo "Step 5: Creating quick test script..."
cat > tests/option2/quick_test.sh << 'QUICKTEST'
#!/bin/bash
cd "$(dirname "$0")"
echo "Running QUICK test mode..."
python run_tests.py --quick --email biomarkerextract@test.com
QUICKTEST
chmod +x tests/option2/quick_test.sh
echo "✓ quick_test.sh created"
echo ""

echo "Step 6: Creating full test script..."
cat > tests/option2/full_test.sh << 'FULLTEST'
#!/bin/bash
cd "$(dirname "$0")"
echo "Running FULL test mode..."
python run_tests.py --email biomarkerextract@test.com
FULLTEST
chmod +x tests/option2/full_test.sh
echo "✓ full_test.sh created"
echo ""

echo "Step 7: System check..."
python << 'SYSCHECK'
import sys
print(f"Python version: {sys.version.split()[0]}")

try:
    from langextract.core import biomarker_models
    print("✓ Phase 3 models available")
except ImportError:
    print("✗ Phase 3 models not found")

try:
    from langextract.literature import batch_processor
    print("✓ Phase 4 literature available")
except ImportError:
    print("✗ Phase 4 literature not found")

try:
    import validation_dataset
    print("✓ Validation dataset loadable")
except ImportError:
    print("✗ Validation dataset not found")
SYSCHECK
echo ""

echo "======================================================================"
echo "Installation Summary"
echo "======================================================================"
echo ""
echo "Files installed:"
echo "  • tests/option2/validation_dataset.py"
echo "  • tests/option2/test_biomarker_categories.py"
echo "  • tests/option2/benchmark_suite.py"
echo "  • tests/option2/accuracy_metrics.py"
echo "  • tests/option2/run_tests.py"
echo "  • tests/option2/README.md"
echo ""
echo "Helper scripts:"
echo "  • tests/option2/quick_test.sh - Run quick tests (~5 min)"
echo "  • tests/option2/full_test.sh  - Run full tests (~15 min)"
echo ""
echo "Results directory:"
echo "  • test_results/ - JSON results saved here"
echo ""
echo "======================================================================"
echo "How to Run Tests"
echo "======================================================================"
echo ""
echo "Option 1: Quick Test (Recommended)"
echo "  cd tests/option2"
echo "  bash quick_test.sh"
echo ""
echo "Option 2: Full Test"
echo "  cd tests/option2"
echo "  bash full_test.sh"
echo ""
echo "Option 3: Custom"
echo "  cd tests/option2"
echo "  python run_tests.py --help"
echo ""
echo "======================================================================"
echo "Option 2: Testing & Refinement - READY ✓"
echo "======================================================================"
echo ""
echo "Next: Run tests to validate system performance and accuracy"
echo ""
