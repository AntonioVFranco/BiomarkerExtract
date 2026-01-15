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

"""Comprehensive test suite for biomarker categories and extraction accuracy."""

from __future__ import annotations

import time
from typing import Dict, List

from langextract.literature import batch_processor
from langextract.core import biomarker_models as bm


class BiomarkerCategoryTester:
  """Test suite for different biomarker categories."""
  
  CATEGORY_QUERIES = {
      bm.BiomarkerCategory.EPIGENETIC: [
          "Horvath clock aging",
          "DNA methylation age",
          "epigenetic clock validation",
          "PhenoAge biomarker",
          "GrimAge mortality"
      ],
      bm.BiomarkerCategory.PROTEOMIC: [
          "GDF-15 aging biomarker",
          "plasma protein aging",
          "CRP inflammation aging",
          "IL-6 cytokine aging",
          "albumin protein homeostasis"
      ],
      bm.BiomarkerCategory.METABOLOMIC: [
          "NAD+ aging metabolism",
          "NMN aging precursor",
          "metabolite aging profile",
          "amino acid aging ratio",
          "lipid peroxidation aging"
      ],
      bm.BiomarkerCategory.GENOMIC: [
          "telomere length aging",
          "clonal hematopoiesis aging",
          "mtDNA mutations aging",
          "somatic mutations accumulation",
          "telomere attrition biomarker"
      ],
      bm.BiomarkerCategory.TRANSCRIPTOMIC: [
          "gene expression aging signature",
          "SASP senescence secretory",
          "inflammatory gene aging",
          "RNA modifications aging",
          "transcriptome aging profile"
      ],
      bm.BiomarkerCategory.CELLULAR: [
          "p16INK4a senescence marker",
          "SA-beta-gal senescence",
          "cellular senescence biomarker",
          "CD4 CD8 ratio aging",
          "immunosenescence markers"
      ]
  }
  
  def __init__(self, pubmed_email: str, pubmed_api_key: str = None):
    """Initialize tester with PubMed credentials."""
    self.processor = batch_processor.LiteratureBatchProcessor(
        pubmed_email=pubmed_email,
        pubmed_api_key=pubmed_api_key,
        max_workers=5
    )
    self.results = {}
  
  def test_category(
      self,
      category: bm.BiomarkerCategory,
      papers_per_query: int = 5
  ) -> Dict:
    """Test biomarker extraction for specific category.
    
    Args:
      category: Biomarker category to test.
      papers_per_query: Number of papers per search query.
    
    Returns:
      Dictionary with test results.
    """
    print(f"\n{'='*60}")
    print(f"Testing Category: {category.value.upper()}")
    print(f"{'='*60}")
    
    queries = self.CATEGORY_QUERIES.get(category, [])
    if not queries:
      print(f"No queries defined for {category.value}")
      return {}
    
    category_results = {
        "category": category.value,
        "queries_tested": 0,
        "papers_found": 0,
        "papers_with_abstracts": 0,
        "potential_biomarkers": 0,
        "queries": []
    }
    
    for query in queries:
      print(f"\nQuery: {query}")
      
      try:
        result = self.processor.search_and_retrieve(
            query=query,
            max_results=papers_per_query,
            include_preprints=False
        )
        
        papers_found = len(result.papers)
        papers_with_abstracts = sum(
            1 for p in result.papers
            if p.metadata.abstract and len(p.metadata.abstract) > 100
        )
        
        print(f"  Papers found: {papers_found}")
        print(f"  With abstracts: {papers_with_abstracts}")
        
        category_results["queries_tested"] += 1
        category_results["papers_found"] += papers_found
        category_results["papers_with_abstracts"] += papers_with_abstracts
        
        category_results["queries"].append({
            "query": query,
            "papers_found": papers_found,
            "papers_with_abstracts": papers_with_abstracts,
            "success": papers_found > 0
        })
        
        time.sleep(1)
        
      except Exception as e:
        print(f"  Error: {e}")
        category_results["queries"].append({
            "query": query,
            "error": str(e),
            "success": False
        })
    
    success_rate = sum(
        1 for q in category_results["queries"] if q.get("success")
    ) / len(queries) * 100 if queries else 0
    
    print(f"\nCategory Summary:")
    print(f"  Queries tested: {category_results['queries_tested']}")
    print(f"  Total papers: {category_results['papers_found']}")
    print(f"  With abstracts: {category_results['papers_with_abstracts']}")
    print(f"  Success rate: {success_rate:.1f}%")
    
    self.results[category.value] = category_results
    return category_results
  
  def test_all_categories(
      self,
      papers_per_query: int = 3
  ) -> Dict:
    """Test all biomarker categories.
    
    Args:
      papers_per_query: Papers to retrieve per query.
    
    Returns:
      Complete test results for all categories.
    """
    print("="*60)
    print("COMPREHENSIVE BIOMARKER CATEGORY TESTING")
    print("="*60)
    
    start_time = time.time()
    
    for category in bm.BiomarkerCategory:
      self.test_category(category, papers_per_query)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("OVERALL SUMMARY")
    print(f"{'='*60}")
    print(f"Total time: {elapsed:.1f}s")
    print(f"Categories tested: {len(self.results)}")
    
    total_papers = sum(r["papers_found"] for r in self.results.values())
    total_abstracts = sum(
        r["papers_with_abstracts"] for r in self.results.values()
    )
    
    print(f"Total papers found: {total_papers}")
    print(f"Papers with abstracts: {total_abstracts}")
    print(f"Abstract coverage: {total_abstracts/total_papers*100:.1f}%")
    
    return {
        "categories": self.results,
        "summary": {
            "total_time": elapsed,
            "total_papers": total_papers,
            "total_with_abstracts": total_abstracts,
            "abstract_coverage": total_abstracts / total_papers if total_papers else 0
        }
    }
  
  def test_specific_biomarkers(self) -> Dict:
    """Test extraction of well-known specific biomarkers.
    
    Returns:
      Results for specific biomarker tests.
    """
    print("\n" + "="*60)
    print("TESTING SPECIFIC WELL-KNOWN BIOMARKERS")
    print("="*60)
    
    specific_tests = [
        ("Horvath Clock", "Horvath DNA methylation clock"),
        ("GrimAge", "GrimAge epigenetic mortality"),
        ("DunedinPACE", "DunedinPACE pace of aging"),
        ("GDF-15", "GDF-15 growth differentiation factor aging"),
        ("NAD+", "NAD+ nicotinamide aging"),
        ("Telomere Length", "telomere length aging biomarker"),
        ("p16INK4a", "p16INK4a senescence marker"),
        ("CRP", "C-reactive protein aging inflammation")
    ]
    
    results = []
    
    for biomarker_name, query in specific_tests:
      print(f"\nTesting: {biomarker_name}")
      print(f"Query: {query}")
      
      try:
        result = self.processor.search_and_retrieve(
            query=query,
            max_results=5,
            include_preprints=False
        )
        
        papers = len(result.papers)
        with_abstracts = sum(
            1 for p in result.papers
            if p.metadata.abstract and len(p.metadata.abstract) > 100
        )
        
        print(f"  Found: {papers} papers ({with_abstracts} with abstracts)")
        
        results.append({
            "biomarker": biomarker_name,
            "query": query,
            "papers_found": papers,
            "papers_with_abstracts": with_abstracts,
            "success": papers > 0
        })
        
        time.sleep(1)
        
      except Exception as e:
        print(f"  Error: {e}")
        results.append({
            "biomarker": biomarker_name,
            "query": query,
            "error": str(e),
            "success": False
        })
    
    success_count = sum(1 for r in results if r.get("success"))
    success_rate = success_count / len(specific_tests) * 100
    
    print(f"\n{'='*60}")
    print("SPECIFIC BIOMARKERS SUMMARY")
    print(f"{'='*60}")
    print(f"Biomarkers tested: {len(specific_tests)}")
    print(f"Successfully found: {success_count}")
    print(f"Success rate: {success_rate:.1f}%")
    
    return {
        "biomarkers": results,
        "summary": {
            "total_tested": len(specific_tests),
            "successful": success_count,
            "success_rate": success_rate
        }
    }


def run_comprehensive_tests(
    pubmed_email: str,
    pubmed_api_key: str = None
) -> Dict:
  """Run all comprehensive tests.
  
  Args:
    pubmed_email: Email for PubMed API.
    pubmed_api_key: Optional API key.
  
  Returns:
    Complete test results.
  """
  tester = BiomarkerCategoryTester(pubmed_email, pubmed_api_key)
  
  category_results = tester.test_all_categories(papers_per_query=3)
  
  specific_results = tester.test_specific_biomarkers()
  
  return {
      "category_tests": category_results,
      "specific_biomarker_tests": specific_results
  }


if __name__ == "__main__":
  results = run_comprehensive_tests(
      pubmed_email="biomarkerextract@test.com"
  )
  
  print("\n" + "="*60)
  print("ALL TESTS COMPLETE")
  print("="*60)
