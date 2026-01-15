#!/bin/bash

# BiomarkerExtract - Automated Phase 2 Files Organization
# Organizes analysis files from Downloads into correct project structure

echo "=========================================="
echo "BiomarkerExtract Phase 2 File Organization"
echo "=========================================="
echo ""

# Navigate to project root
cd /mnt/c/Users/tommo/Documents/Bioinformatics/1102/BiomarkerExtract

# Check if Downloads directory exists
DOWNLOADS_DIR="/mnt/c/Users/tommo/Documents/Bioinformatics/1102/Downloads"
if [ ! -d "$DOWNLOADS_DIR" ]; then
    echo "Error: Downloads directory not found at $DOWNLOADS_DIR"
    exit 1
fi

echo "Step 1: Creating project directories..."
mkdir -p docs/analysis
mkdir -p scripts/analysis
echo "✓ Directories created"
echo ""

echo "Step 2: Moving documentation..."
if [ -f "$DOWNLOADS_DIR/BiomarkerExtract_Phase2_Analysis.md" ]; then
    mv "$DOWNLOADS_DIR/BiomarkerExtract_Phase2_Analysis.md" docs/analysis/
    echo "✓ Moved BiomarkerExtract_Phase2_Analysis.md to docs/analysis/"
else
    echo "⚠ BiomarkerExtract_Phase2_Analysis.md not found in Downloads"
fi
echo ""

echo "Step 3: Moving Python analysis script..."
if [ -f "$DOWNLOADS_DIR/analyze_code_structure.py" ]; then
    mv "$DOWNLOADS_DIR/analyze_code_structure.py" scripts/analysis/
    chmod +x scripts/analysis/analyze_code_structure.py
    echo "✓ Moved analyze_code_structure.py to scripts/analysis/"
else
    echo "⚠ analyze_code_structure.py not found in Downloads"
fi
echo ""

echo "Step 4: Moving bash scripts..."
if [ -f "$DOWNLOADS_DIR/phase2_commands.sh" ]; then
    mv "$DOWNLOADS_DIR/phase2_commands.sh" scripts/analysis/
    chmod +x scripts/analysis/phase2_commands.sh
    echo "✓ Moved phase2_commands.sh to scripts/analysis/"
else
    echo "⚠ phase2_commands.sh not found in Downloads"
fi

if [ -f "$DOWNLOADS_DIR/analyze_architecture.sh" ]; then
    mv "$DOWNLOADS_DIR/analyze_architecture.sh" scripts/analysis/
    chmod +x scripts/analysis/analyze_architecture.sh
    echo "✓ Moved analyze_architecture.sh to scripts/analysis/"
else
    echo "⚠ analyze_architecture.sh not found in Downloads"
fi
echo ""

echo "Step 5: Verifying organization..."
echo ""
echo "Documentation:"
ls -lh docs/analysis/
echo ""
echo "Analysis Scripts:"
ls -lh scripts/analysis/
echo ""

echo "=========================================="
echo "Organization Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run architecture analysis: python scripts/analysis/analyze_code_structure.py"
echo "2. Run Phase 2 commands: bash scripts/analysis/phase2_commands.sh"
echo "3. Review documentation: cat docs/analysis/BiomarkerExtract_Phase2_Analysis.md"
echo ""
echo "Ready to proceed to Phase 3 implementation!"
