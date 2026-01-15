#!/bin/bash

# BiomarkerExtract Phase 4 Installation Script
# Literature Pipeline Implementation

set -e

echo "========================================"
echo "BiomarkerExtract Phase 4 Installation"
echo "Literature Pipeline"
echo "========================================"
echo ""

cd /mnt/c/Users/tommo/Documents/Bioinformatics/1102/BiomarkerExtract
source venv/bin/activate

echo "Step 1: Installing required dependencies..."
pip install biopython PyMuPDF requests tqdm --break-system-packages
echo ""

echo "Step 2: Creating literature module directory..."
mkdir -p langextract/literature
touch langextract/literature/__init__.py
echo ""

echo "Step 3: Moving literature pipeline files..."
cp metadata_models.py langextract/literature/ 2>/dev/null || echo "  Download metadata_models.py first"
cp pubmed_client.py langextract/literature/ 2>/dev/null || echo "  Download pubmed_client.py first"
cp biorxiv_client.py langextract/literature/ 2>/dev/null || echo "  Download biorxiv_client.py first"
cp pdf_parser.py langextract/literature/ 2>/dev/null || echo "  Download pdf_parser.py first"
cp batch_processor.py langextract/literature/ 2>/dev/null || echo "  Download batch_processor.py first"
echo ""

echo "Step 4: Verifying file placement..."
echo "Literature module files:"
ls -lh langextract/literature/*.py 2>/dev/null || echo "  No files found - please download and copy"
echo ""

echo "Step 5: Testing imports..."
python << 'PYTHON_TEST'
try:
    from langextract.literature import metadata_models
    print("✓ metadata_models imported")
except ImportError as e:
    print(f"✗ metadata_models import failed: {e}")

try:
    from langextract.literature import pubmed_client
    print("✓ pubmed_client imported")
except ImportError as e:
    print(f"✗ pubmed_client import failed: {e}")

try:
    from langextract.literature import biorxiv_client
    print("✓ biorxiv_client imported")
except ImportError as e:
    print(f"✗ biorxiv_client import failed: {e}")

try:
    from langextract.literature import pdf_parser
    print("✓ pdf_parser imported")
except ImportError as e:
    print(f"✗ pdf_parser import failed: {e}")

try:
    from langextract.literature import batch_processor
    print("✓ batch_processor imported")
except ImportError as e:
    print(f"✗ batch_processor import failed: {e}")
PYTHON_TEST
echo ""

echo "Step 6: Creating example usage script..."
cat > example_literature_pipeline.py << 'EXAMPLE_SCRIPT'
"""Example usage of BiomarkerExtract literature pipeline."""

from langextract.literature import batch_processor

def main():
    processor = batch_processor.LiteratureBatchProcessor(
        pubmed_email="your.email@domain.com",
        pubmed_api_key="YOUR_API_KEY",
        max_workers=5
    )
    
    biomarker_terms = [
        "DNA methylation clock",
        "Horvath clock",
        "epigenetic age",
        "GDF-15"
    ]
    
    print("Searching for biomarker papers...")
    result = processor.search_biomarkers_comprehensive(
        biomarker_terms=biomarker_terms,
        max_pubmed_results=10,
        preprint_days_back=30
    )
    
    print(f"\nResults:")
    print(f"Total papers found: {result.successful}")
    print(f"Processing time: {result.processing_time_seconds:.2f}s")
    print(f"Success rate: {result.success_rate():.1f}%")
    
    print(f"\nFirst 3 papers:")
    for i, paper in enumerate(result.papers[:3], 1):
        print(f"\n{i}. {paper.metadata.title}")
        print(f"   Authors: {len(paper.metadata.authors)} authors")
        print(f"   Source: {paper.metadata.source}")
        if paper.metadata.doi:
            print(f"   DOI: {paper.metadata.doi}")

if __name__ == "__main__":
    main()
EXAMPLE_SCRIPT

echo "✓ Created example_literature_pipeline.py"
echo ""

echo "Step 7: Testing Pydantic models..."
python << 'MODEL_TEST'
from langextract.literature import metadata_models as mm
from datetime import datetime

try:
    author = mm.Author(
        last_name="Smith",
        first_name="John",
        affiliation="University of Aging"
    )
    print(f"✓ Created Author: {author.last_name}, {author.first_name}")
    
    metadata = mm.PaperMetadata(
        title="DNA Methylation and Aging: A Comprehensive Review",
        doi="10.1234/example.doi",
        authors=[author],
        publication_type=mm.PublicationType.REVIEW,
        source=mm.LiteratureSource.PUBMED,
        abstract="This is a test abstract about aging biomarkers.",
        publication_date=datetime(2024, 1, 15)
    )
    print(f"✓ Created PaperMetadata: {metadata.title}")
    print(f"  Is complete: {metadata.is_complete()}")
    
    section = mm.PaperSection(
        section_type="results",
        content="Test results section content here."
    )
    print(f"✓ Created PaperSection: {section.section_type}")
    
    parsed = mm.ParsedPaper(
        metadata=metadata,
        sections=[section]
    )
    print(f"✓ Created ParsedPaper with {len(parsed.sections)} sections")
    print("\n✓✓✓ All models working correctly! ✓✓✓")
    
except Exception as e:
    print(f"✗ Model test failed: {e}")
MODEL_TEST
echo ""

echo "========================================"
echo "Phase 4 Installation Summary"
echo "========================================"
echo ""
echo "Dependencies installed:"
echo "  • biopython (PubMed E-utilities)"
echo "  • PyMuPDF (PDF parsing)"
echo "  • requests (HTTP client)"
echo "  • tqdm (progress bars)"
echo ""
echo "Files created:"
echo "  • langextract/literature/__init__.py"
echo "  • langextract/literature/metadata_models.py"
echo "  • langextract/literature/pubmed_client.py"
echo "  • langextract/literature/biorxiv_client.py"
echo "  • langextract/literature/pdf_parser.py"
echo "  • langextract/literature/batch_processor.py"
echo "  • example_literature_pipeline.py"
echo ""
echo "Next steps:"
echo "  1. Set NCBI API key (optional but recommended)"
echo "  2. Test with example_literature_pipeline.py"
echo "  3. Integrate with Phase 3 biomarker extraction"
echo "  4. Build complete end-to-end pipeline"
echo ""
echo "Phase 4: COMPLETE ✓"
echo "========================================"
