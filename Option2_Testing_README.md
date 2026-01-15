# BiomarkerExtract - Option 2: Testing & Refinement

Complete testing and validation suite for biomarker extraction accuracy, performance benchmarking, and quality assessment.

---

## Overview

This testing suite validates BiomarkerExtract across 3 critical dimensions:

1. **Category Coverage** - Tests all 6 biomarker categories
2. **Performance** - Benchmarks speed and throughput
3. **Accuracy** - Validates extraction quality against golden dataset

---

## Files Created

### 1. `validation_dataset.py` (270 lines)
**Golden Dataset** of 10 well-known aging biomarkers:

**Biomarkers included:**
- Horvath Clock (2013) - Epigenetic
- GrimAge (2019) - Epigenetic
- DunedinPACE (2022) - Epigenetic
- PhenoAge (2018) - Epigenetic
- GDF-15 (2017) - Proteomic
- NAD+/NADH Ratio (2016) - Metabolomic
- Telomere Length (2012) - Genomic
- p16INK4a (2015) - Cellular
- C-Reactive Protein (2013) - Proteomic
- IL-6 (2018) - Proteomic

**Features:**
- Expected ontology terms (GO, KEGG, UniProt)
- Validation studies (PMIDs)
- Search queries for testing
- Export to JSON

---

### 2. `test_biomarker_categories.py` (330 lines)
**Comprehensive Category Testing:**

Tests all 6 biomarker categories:
- Epigenetic (5 queries)
- Proteomic (5 queries)
- Metabolomic (5 queries)
- Genomic (5 queries)
- Transcriptomic (5 queries)
- Cellular (5 queries)

**Plus specific biomarker tests:**
- 8 well-known biomarkers
- Real PubMed searches
- Abstract coverage metrics

---

### 3. `benchmark_suite.py` (320 lines)
**Performance Benchmarking:**

**Tests:**
- PubMed search speed
- Abstract fetching throughput
- Batch processing performance
- Rate limiting effectiveness
- bioRxiv preprint fetching

**Metrics:**
- Queries per second
- Papers per second
- Time per operation
- Success rates

---

### 4. `accuracy_metrics.py` (310 lines)
**Accuracy Calculation:**

**Metrics:**
- Category classification accuracy
- Ontology precision/recall/F1
- Validation detection accuracy
- Confidence-quality correlation
- Confusion matrix

**Scoring:**
- Overall quality score (0-100)
- Grade assignment (Excellent/Good/Fair/Needs Improvement)
- Per-category metrics

---

### 5. `run_tests.py` (230 lines)
**Master Test Runner:**

Orchestrates all tests with:
- Command-line interface
- Quick vs Full mode
- Selective test execution
- JSON results export
- Final summary report

---

## Installation

```bash
cd /mnt/c/Users/tommo/Documents/Bioinformatics/1102/BiomarkerExtract
source venv/bin/activate

# Copy test files to tests/ directory
mkdir -p tests/option2
cp validation_dataset.py tests/option2/
cp test_biomarker_categories.py tests/option2/
cp benchmark_suite.py tests/option2/
cp accuracy_metrics.py tests/option2/
cp run_tests.py tests/option2/
chmod +x tests/option2/run_tests.py
```

---

## Usage

### Quick Test (Recommended First Run)

```bash
cd tests/option2
python run_tests.py --quick
```

**Quick mode:**
- 1 query per category
- ~5 minutes runtime
- Good for validation

### Full Test

```bash
python run_tests.py
```

**Full mode:**
- 3 queries per category
- ~15 minutes runtime
- Comprehensive testing

### Selective Tests

```bash
# Only validation dataset
python run_tests.py --skip-categories --skip-benchmarks

# Only category testing
python run_tests.py --skip-validation --skip-benchmarks

# Only benchmarks
python run_tests.py --skip-validation --skip-categories

# Custom email
python run_tests.py --email your.email@domain.com
```

---

## Expected Results

### Phase 1: Validation Dataset
```
Total biomarkers: 10
Total search queries: 30
Year range: 2012-2022

By category:
  epigenetic: 4
  proteomic: 3
  metabolomic: 1
  genomic: 1
  cellular: 1
```

### Phase 2: Category Testing
```
Categories tested: 6
Total papers found: 60-100
Papers with abstracts: 50-90
Abstract coverage: >80%
Success rate: >90%
```

### Phase 3: Performance Benchmarks
```
PubMed search: 2-5 PMIDs/s
Abstract fetching: 1-3 papers/s
Batch processing: >90% success
Rate limiting: Working correctly
```

---

## Interpreting Results

### Success Criteria

**Category Testing:**
- ✅ Success rate > 90%
- ✅ Abstract coverage > 80%
- ✅ All categories returning papers

**Performance:**
- ✅ PubMed: 2+ PMIDs/s
- ✅ Abstracts: 1+ paper/s
- ✅ Rate limiting: functional

**Quality:**
- ✅ Papers with valid metadata
- ✅ Abstracts > 100 characters
- ✅ Authors present

---

## Test Results Storage

Results saved to `test_results/` directory:

```
test_results/
├── test_results_20260114_235900.json
├── test_results_20260115_001200.json
└── ...
```

**JSON structure:**
```json
{
  "validation_dataset": {...},
  "category_tests": {
    "category_results": {...},
    "specific_results": {...}
  },
  "benchmarks": {...},
  "metadata": {
    "total_time": 450.2,
    "end_time": "2026-01-15T00:12:00",
    "mode": "full"
  }
}
```

---

## Troubleshooting

### PubMed Rate Limiting
```bash
# If getting rate limit errors, use API key
export PUBMED_API_KEY="your-key"
python run_tests.py
```

### Network Errors
```bash
# Reduce parallelism
# Edit batch_processor.py: max_workers=3
```

### Timeouts
```bash
# Run quick mode or selective tests
python run_tests.py --quick --skip-benchmarks
```

---

## Advanced Usage

### Validation Dataset Export

```python
from validation_dataset import ValidationDataset

dataset = ValidationDataset()
dataset.export_to_json("biomarkers_golden.json")
```

### Custom Category Test

```python
from test_biomarker_categories import BiomarkerCategoryTester
from langextract.core import biomarker_models as bm

tester = BiomarkerCategoryTester("your.email@domain.com")
results = tester.test_category(
    bm.BiomarkerCategory.EPIGENETIC,
    papers_per_query=5
)
```

### Custom Benchmark

```python
from benchmark_suite import PerformanceBenchmark

benchmark = PerformanceBenchmark("your.email@domain.com")
results = benchmark.benchmark_pubmed_search(
    queries=["custom query 1", "custom query 2"],
    max_results=20
)
```

---

## Metrics Explained

### Category Accuracy
Percentage of biomarkers correctly classified into categories.

### Ontology Precision
Of extracted ontology terms, what % are correct?

### Ontology Recall
Of expected ontology terms, what % were extracted?

### F1 Score
Harmonic mean of precision and recall (0-1).

### Validation Accuracy
Percentage correctly identifying validated biomarkers.

### Confidence Correlation
How well confidence scores predict quality (0-1).

---

## Next Steps After Testing

### If Results Are Good (>85% metrics):
✅ Proceed to **Option 1: Production Pipeline**
- Integrate real Gemini extraction
- Automated pipeline
- Scale to 1000+ papers

### If Results Need Improvement (<85%):
📊 **Refinement Actions:**
1. Adjust search queries
2. Improve ontology mappings
3. Tune confidence thresholds
4. Expand validation dataset

---

## Test Timeline

**Quick Mode:** ~5 minutes
- Validation dataset: 10 seconds
- Category testing: 3 minutes
- Benchmarks: 2 minutes

**Full Mode:** ~15 minutes
- Validation dataset: 10 seconds
- Category testing: 10 minutes
- Benchmarks: 5 minutes

---

## Success Metrics Summary

| Metric | Target | Good | Excellent |
|--------|--------|------|-----------|
| Category Success Rate | >80% | >90% | >95% |
| Abstract Coverage | >70% | >80% | >90% |
| PubMed Throughput | >1 PMID/s | >3 PMID/s | >5 PMID/s |
| Abstract Fetch | >0.5 paper/s | >1 paper/s | >2 paper/s |
| Category Accuracy | >70% | >85% | >95% |
| Ontology F1 | >0.60 | >0.75 | >0.85 |

---

**Status:** Ready for execution
**Estimated Time:** 5-15 minutes depending on mode
**Requirements:** Active internet, PubMed access

---

## Example Output

```
======================================================================
BIOMARKEREXTRACT TESTING & REFINEMENT SUITE
Option 2: Testing & Refinement
======================================================================

Start time: 2026-01-15 00:00:00
Email: biomarkerextract@test.com
Mode: QUICK

======================================================================
PHASE 1: VALIDATION DATASET
======================================================================

Total biomarkers: 10
Total search queries: 30
Year range: 2012-2022

======================================================================
PHASE 2: BIOMARKER CATEGORY TESTING
======================================================================

Testing Category: EPIGENETIC
...
Papers found: 15
Success rate: 100.0%

======================================================================
PHASE 3: PERFORMANCE BENCHMARKING
======================================================================

PubMed Search: 3.2 PMIDs/s
Abstract Fetching: 1.5 papers/s
Batch Processing: 95.0% success

======================================================================
FINAL SUMMARY
======================================================================

✓ Phase 1: Validation Dataset - COMPLETE
✓ Phase 2: Category Testing - COMPLETE
  Total papers found: 85
  Papers with abstracts: 72
✓ Phase 3: Performance Benchmarks - COMPLETE
  PubMed throughput: 3.2 PMIDs/s
  Batch processing: 95.0% success

STATUS: TESTING & REFINEMENT COMPLETE ✓

Next step: OPTION 1 - Production Pipeline with Gemini

Total execution time: 312.5s
```

---

**Ready to run!** Execute `python run_tests.py --quick` to begin! 🚀
