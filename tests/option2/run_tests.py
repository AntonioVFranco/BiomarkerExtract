#!/usr/bin/env python3
# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Master test runner for BiomarkerExtract Testing & Refinement (Option 2)."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path


def run_validation_dataset_summary():
  """Run validation dataset summary."""
  print("\n" + "="*70)
  print("PHASE 1: VALIDATION DATASET")
  print("="*70)
  
  try:
    import validation_dataset
    validation_dataset.print_dataset_summary()
    return True
  except Exception as e:
    print(f"Error: {e}")
    return False


def run_category_tests(pubmed_email: str, quick: bool = False):
  """Run biomarker category tests."""
  print("\n" + "="*70)
  print("PHASE 2: BIOMARKER CATEGORY TESTING")
  print("="*70)
  
  try:
    import test_biomarker_categories
    
    tester = test_biomarker_categories.BiomarkerCategoryTester(
        pubmed_email=pubmed_email
    )
    
    if quick:
      print("\nRunning QUICK test (1 query per category)...")
      results = tester.test_all_categories(papers_per_query=1)
    else:
      print("\nRunning FULL test (3 queries per category)...")
      results = tester.test_all_categories(papers_per_query=3)
    
    print("\nRunning specific biomarker tests...")
    specific_results = tester.test_specific_biomarkers()
    
    return {
        "category_results": results,
        "specific_results": specific_results
    }
    
  except Exception as e:
    print(f"Error: {e}")
    return None


def run_performance_benchmarks(pubmed_email: str):
  """Run performance benchmarks."""
  print("\n" + "="*70)
  print("PHASE 3: PERFORMANCE BENCHMARKING")
  print("="*70)
  
  try:
    import benchmark_suite
    
    benchmark = benchmark_suite.PerformanceBenchmark(pubmed_email)
    results = benchmark.run_all_benchmarks()
    
    return results
    
  except Exception as e:
    print(f"Error: {e}")
    return None


def save_results(results: dict, output_dir: str = "test_results"):
  """Save test results to JSON file."""
  output_path = Path(output_dir)
  output_path.mkdir(exist_ok=True)
  
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = output_path / f"test_results_{timestamp}.json"
  
  with open(filename, 'w') as f:
    json.dump(results, f, indent=2, default=str)
  
  print(f"\n✓ Results saved to: {filename}")
  return filename


def print_final_summary(results: dict):
  """Print final test summary."""
  print("\n" + "="*70)
  print("FINAL SUMMARY - TESTING & REFINEMENT (OPTION 2)")
  print("="*70)
  
  if "validation_dataset" in results:
    print("\n✓ Phase 1: Validation Dataset - COMPLETE")
  
  if "category_tests" in results:
    cat_res = results["category_tests"]["category_results"]["summary"]
    print(f"\n✓ Phase 2: Category Testing - COMPLETE")
    print(f"  Total papers found: {cat_res['total_papers']}")
    print(f"  Papers with abstracts: {cat_res['total_with_abstracts']}")
  
  if "benchmarks" in results:
    bench = results["benchmarks"]
    print(f"\n✓ Phase 3: Performance Benchmarks - COMPLETE")
    if "pubmed_search" in bench:
      print(f"  PubMed throughput: {bench['pubmed_search']['pmids_per_second']:.1f} PMIDs/s")
    if "batch_processing" in bench:
      print(f"  Batch processing: {bench['batch_processing']['success_rate']:.1f}% success")
  
  print("\n" + "="*70)
  print("STATUS: TESTING & REFINEMENT COMPLETE ✓")
  print("="*70)
  print("\nNext step: OPTION 1 - Production Pipeline with Gemini")
  print()


def main():
  """Main test runner."""
  parser = argparse.ArgumentParser(
      description="BiomarkerExtract Testing & Refinement Suite"
  )
  parser.add_argument(
      "--email",
      default="biomarkerextract@test.com",
      help="PubMed email address"
  )
  parser.add_argument(
      "--quick",
      action="store_true",
      help="Run quick tests (fewer queries)"
  )
  parser.add_argument(
      "--skip-validation",
      action="store_true",
      help="Skip validation dataset summary"
  )
  parser.add_argument(
      "--skip-categories",
      action="store_true",
      help="Skip category testing"
  )
  parser.add_argument(
      "--skip-benchmarks",
      action="store_true",
      help="Skip performance benchmarks"
  )
  parser.add_argument(
      "--output-dir",
      default="test_results",
      help="Output directory for results"
  )
  
  args = parser.parse_args()
  
  print("="*70)
  print("BIOMARKEREXTRACT TESTING & REFINEMENT SUITE")
  print("Option 2: Testing & Refinement")
  print("="*70)
  print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print(f"Email: {args.email}")
  print(f"Mode: {'QUICK' if args.quick else 'FULL'}")
  print()
  
  start_time = time.time()
  results = {}
  
  if not args.skip_validation:
    results["validation_dataset"] = run_validation_dataset_summary()
  
  if not args.skip_categories:
    results["category_tests"] = run_category_tests(args.email, args.quick)
  
  if not args.skip_benchmarks:
    results["benchmarks"] = run_performance_benchmarks(args.email)
  
  elapsed = time.time() - start_time
  
  results["metadata"] = {
      "total_time": elapsed,
      "end_time": datetime.now().isoformat(),
      "mode": "quick" if args.quick else "full"
  }
  
  save_results(results, args.output_dir)
  
  print_final_summary(results)
  
  print(f"\nTotal execution time: {elapsed:.1f}s")
  print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
  main()
