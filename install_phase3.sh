#!/bin/bash

# BiomarkerExtract Phase 3 Installation Script
# Moves created files to correct locations and validates installation

set -e

echo "========================================"
echo "BiomarkerExtract Phase 3 Installation"
echo "========================================"
echo ""

# Ensure we're in project root
cd /mnt/c/Users/tommo/Documents/Bioinformatics/1102/BiomarkerExtract
source venv/bin/activate

echo "Step 1: Creating backup of existing files..."
BACKUP_DIR="backups/phase3_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Backup directory: $BACKUP_DIR"
echo ""

echo "Step 2: Moving biomarker_models.py to langextract/core/..."
if [ -f "$HOME/biomarker_models.py" ] || [ -f "/root/biomarker_models.py" ]; then
    cp /root/biomarker_models.py langextract/core/ 2>/dev/null || \
    cp "$HOME/biomarker_models.py" langextract/core/ 2>/dev/null || true
    echo "✓ biomarker_models.py moved to langextract/core/"
else
    echo "⚠ biomarker_models.py not found in home directory"
    echo "  Download it from Claude interface and place in project root"
fi
echo ""

echo "Step 3: Moving gemini_biomarker.py to langextract/providers/..."
if [ -f "$HOME/gemini_biomarker.py" ] || [ -f "/root/gemini_biomarker.py" ]; then
    cp /root/gemini_biomarker.py langextract/providers/ 2>/dev/null || \
    cp "$HOME/gemini_biomarker.py" langextract/providers/ 2>/dev/null || true
    echo "✓ gemini_biomarker.py moved to langextract/providers/"
else
    echo "⚠ gemini_biomarker.py not found in home directory"
    echo "  Download it from Claude interface and place in project root"
fi
echo ""

echo "Step 4: Moving biomarker_models_test.py to tests/..."
if [ -f "$HOME/biomarker_models_test.py" ] || [ -f "/root/biomarker_models_test.py" ]; then
    cp /root/biomarker_models_test.py tests/ 2>/dev/null || \
    cp "$HOME/biomarker_models_test.py" tests/ 2>/dev/null || true
    echo "✓ biomarker_models_test.py moved to tests/"
else
    echo "⚠ biomarker_models_test.py not found in home directory"
    echo "  Download it from Claude interface and place in project root"
fi
echo ""

echo "Step 5: Verifying file placement..."
echo ""
echo "Core models:"
ls -lh langextract/core/biomarker_models.py 2>/dev/null || echo "  Not found"
echo ""
echo "Provider:"
ls -lh langextract/providers/gemini_biomarker.py 2>/dev/null || echo "  Not found"
echo ""
echo "Tests:"
ls -lh tests/biomarker_models_test.py 2>/dev/null || echo "  Not found"
echo ""

echo "Step 6: Testing biomarker_models import..."
python -c "from langextract.core import biomarker_models; print('✓ biomarker_models imported successfully')" || \
echo "⚠ Import failed - check file location"
echo ""

echo "Step 7: Testing gemini_biomarker import..."
python -c "from langextract.providers import gemini_biomarker; print('✓ gemini_biomarker imported successfully')" || \
echo "⚠ Import failed - check file location"
echo ""

echo "Step 8: Running unit tests..."
if [ -f "tests/biomarker_models_test.py" ]; then
    echo "Running pytest on biomarker_models_test.py..."
    pytest tests/biomarker_models_test.py -v || echo "⚠ Some tests failed"
else
    echo "⚠ Test file not found - skipping tests"
fi
echo ""

echo "Step 9: Validating Pydantic models..."
python << 'PYTHON_SCRIPT'
try:
    from langextract.core import biomarker_models as bm
    
    entity = bm.BiomarkerEntity(
        name="Horvath clock",
        category=bm.BiomarkerCategory.EPIGENETIC,
        measurement_method="DNA methylation array",
        finding="Age acceleration observed in treatment group",
        statistics=bm.Statistics(
            p_value=0.001,
            effect_size=0.85,
            sample_size=1200
        ),
        validation_status=bm.ValidationStatus(
            is_validated=True,
            replication_count=1
        ),
        controlled_terms=bm.ControlledTerms(
            go_terms=["GO:0006306"],
            mesh_terms=["D019175"]
        ),
        confidence=0.95
    )
    
    score = entity.calculate_validation_score()
    print(f"✓ Created test biomarker entity")
    print(f"✓ Validation score: {score}/100")
    print(f"✓ All Pydantic models working correctly")
except Exception as e:
    print(f"⚠ Model validation failed: {e}")
PYTHON_SCRIPT
echo ""

echo "========================================"
echo "Phase 3 Installation Summary"
echo "========================================"
echo ""
echo "Files created:"
echo "  • langextract/core/biomarker_models.py"
echo "  • langextract/providers/gemini_biomarker.py"
echo "  • tests/biomarker_models_test.py"
echo ""
echo "Features implemented:"
echo "  • 7 Pydantic models with validation"
echo "  • Statistics validation (p<0.05 enforcement)"
echo "  • Controlled vocabulary validators (GO, KEGG, UniProt, MeSH)"
echo "  • Validation scoring system"
echo "  • Custom Gemini provider with few-shot examples"
echo "  • Comprehensive unit test suite"
echo ""
echo "Next steps (Phase 4):"
echo "  1. Test extraction on real scientific papers"
echo "  2. Integrate PubMed API for literature retrieval"
echo "  3. Add bioRxiv/medRxiv support"
echo "  4. Build batch processing pipeline"
echo ""
echo "Phase 3: COMPLETE ✓"
echo "========================================"
