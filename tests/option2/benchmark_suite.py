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

"""Performance benchmarking suite for BiomarkerExtract pipeline."""

from __future__ import annotations

import time
from typing import Dict, List

from langextract.literature import batch_processor
from langextract.literature import pubmed_client
from langextract.literature import biorxiv_client


class PerformanceBenchmark:
  """Performance benchmarking for literature pipeline."""
  
  def __init__(self, pubmed_email: str, pubmed_api_key: str = None):
    """Initialize benchmark suite."""
    self.pubmed_email = pubmed_email
    self.pubmed_api_key = pubmed_api_key
    self.results = {}
  
  def benchmark_pubmed_search(
      self,
      queries: List[str],
      max_results: int = 10
  ) -> Dict:
    """Benchmark PubMed search performance.
    
    Args:
      queries: List of search queries.
      max_results: Results per query.
    
    Returns:
      Benchmark results.
    """
    print("\n" + "="*60)
    print("BENCHMARK: PubMed Search Speed")
    print("="*60)
    
    client = pubmed_client.PubMedClient(
        email=self.pubmed_email,
        api_key=self.pubmed_api_key
    )
    
    timings = []
    total_pmids = 0
    
    for query in queries:
      start = time.time()
      pmids = client.search(query, max_results=max_results)
      elapsed = time.time() - start
      
      timings.append(elapsed)
      total_pmids += len(pmids)
      
      print(f"Query: {query[:50]}...")
      print(f"  Time: {elapsed:.2f}s")
      print(f"  PMIDs: {len(pmids)}")
    
    avg_time = sum(timings) / len(timings)
    total_time = sum(timings)
    
    results = {
        "queries_tested": len(queries),
        "total_time": total_time,
        "average_time_per_query": avg_time,
        "total_pmids_found": total_pmids,
        "pmids_per_second": total_pmids / total_time if total_time > 0 else 0
    }
    
    print(f"\nSummary:")
    print(f"  Total queries: {results['queries_tested']}")
    print(f"  Total time: {results['total_time']:.2f}s")
    print(f"  Avg time/query: {results['average_time_per_query']:.2f}s")
    print(f"  PMIDs found: {results['total_pmids_found']}")
    print(f"  Throughput: {results['pmids_per_second']:.1f} PMIDs/s")
    
    self.results["pubmed_search"] = results
    return results
  
  def benchmark_abstract_fetching(
      self,
      pmid_count: int = 50
  ) -> Dict:
    """Benchmark abstract fetching speed.
    
    Args:
      pmid_count: Number of abstracts to fetch.
    
    Returns:
      Benchmark results.
    """
    print("\n" + "="*60)
    print("BENCHMARK: Abstract Fetching Speed")
    print("="*60)
    
    client = pubmed_client.PubMedClient(
        email=self.pubmed_email,
        api_key=self.pubmed_api_key
    )
    
    print(f"Searching for {pmid_count} papers...")
    pmids = client.search(
        query="aging biomarkers",
        max_results=pmid_count
    )
    
    print(f"Fetching {len(pmids)} abstracts...")
    start = time.time()
    papers = client.fetch_abstracts(pmids)
    elapsed = time.time() - start
    
    results = {
        "pmids_requested": len(pmids),
        "papers_retrieved": len(papers),
        "total_time": elapsed,
        "time_per_paper": elapsed / len(papers) if papers else 0,
        "papers_per_second": len(papers) / elapsed if elapsed > 0 else 0
    }
    
    print(f"\nResults:")
    print(f"  Papers retrieved: {results['papers_retrieved']}")
    print(f"  Total time: {results['total_time']:.2f}s")
    print(f"  Time/paper: {results['time_per_paper']:.3f}s")
    print(f"  Throughput: {results['papers_per_second']:.1f} papers/s")
    
    self.results["abstract_fetching"] = results
    return results
  
  def benchmark_batch_processing(
      self,
      biomarker_terms: List[str],
      max_results: int = 10
  ) -> Dict:
    """Benchmark batch processing performance.
    
    Args:
      biomarker_terms: Terms to search.
      max_results: Max results per term.
    
    Returns:
      Benchmark results.
    """
    print("\n" + "="*60)
    print("BENCHMARK: Batch Processing")
    print("="*60)
    
    processor = batch_processor.LiteratureBatchProcessor(
        pubmed_email=self.pubmed_email,
        pubmed_api_key=self.pubmed_api_key,
        max_workers=5
    )
    
    start = time.time()
    result = processor.search_biomarkers_comprehensive(
        biomarker_terms=biomarker_terms,
        max_pubmed_results=max_results,
        preprint_days_back=30
    )
    elapsed = time.time() - start
    
    results = {
        "biomarker_terms": len(biomarker_terms),
        "papers_found": result.successful,
        "total_time": elapsed,
        "time_per_term": elapsed / len(biomarker_terms),
        "papers_per_second": result.successful / elapsed if elapsed > 0 else 0,
        "success_rate": result.success_rate()
    }
    
    print(f"\nResults:")
    print(f"  Terms searched: {results['biomarker_terms']}")
    print(f"  Papers found: {results['papers_found']}")
    print(f"  Total time: {results['total_time']:.2f}s")
    print(f"  Time/term: {results['time_per_term']:.2f}s")
    print(f"  Throughput: {results['papers_per_second']:.1f} papers/s")
    print(f"  Success rate: {results['success_rate']:.1f}%")
    
    self.results["batch_processing"] = results
    return results
  
  def benchmark_rate_limiting(self) -> Dict:
    """Benchmark rate limiting effectiveness.
    
    Returns:
      Rate limiting test results.
    """
    print("\n" + "="*60)
    print("BENCHMARK: Rate Limiting")
    print("="*60)
    
    client = pubmed_client.PubMedClient(
        email=self.pubmed_email,
        api_key=self.pubmed_api_key
    )
    
    expected_rate = client.requests_per_second
    print(f"Expected rate: {expected_rate} req/s")
    print(f"API key: {'Yes' if self.pubmed_api_key else 'No'}")
    
    test_queries = [
        "aging biomarker",
        "DNA methylation",
        "senescence marker",
        "telomere length",
        "NAD+ metabolism"
    ]
    
    start = time.time()
    for query in test_queries:
      client.search(query, max_results=1)
    elapsed = time.time() - start
    
    actual_rate = len(test_queries) / elapsed
    
    results = {
        "expected_rate": expected_rate,
        "actual_rate": actual_rate,
        "requests_made": len(test_queries),
        "total_time": elapsed,
        "rate_limit_working": actual_rate <= expected_rate * 1.1
    }
    
    print(f"\nResults:")
    print(f"  Requests: {results['requests_made']}")
    print(f"  Time: {results['total_time']:.2f}s")
    print(f"  Actual rate: {results['actual_rate']:.2f} req/s")
    print(f"  Rate limit OK: {results['rate_limit_working']}")
    
    self.results["rate_limiting"] = results
    return results
  
  def benchmark_biorxiv(
      self,
      keywords: List[str]
  ) -> Dict:
    """Benchmark bioRxiv preprint fetching.
    
    Args:
      keywords: Keywords to search.
    
    Returns:
      Benchmark results.
    """
    print("\n" + "="*60)
    print("BENCHMARK: bioRxiv Preprint Fetching")
    print("="*60)
    
    client = biorxiv_client.BioRxivClient()
    
    timings = []
    total_papers = 0
    
    for keyword in keywords:
      start = time.time()
      papers = client.search_by_keyword(
          keyword=keyword,
          days_back=30,
          server="biorxiv"
      )
      elapsed = time.time() - start
      
      timings.append(elapsed)
      total_papers += len(papers)
      
      print(f"Keyword: {keyword}")
      print(f"  Time: {elapsed:.2f}s")
      print(f"  Papers: {len(papers)}")
    
    total_time = sum(timings)
    avg_time = total_time / len(keywords)
    
    results = {
        "keywords_searched": len(keywords),
        "total_papers": total_papers,
        "total_time": total_time,
        "avg_time_per_keyword": avg_time,
        "papers_per_second": total_papers / total_time if total_time > 0 else 0
    }
    
    print(f"\nSummary:")
    print(f"  Keywords: {results['keywords_searched']}")
    print(f"  Papers: {results['total_papers']}")
    print(f"  Total time: {results['total_time']:.2f}s")
    print(f"  Avg time: {results['avg_time_per_keyword']:.2f}s")
    print(f"  Throughput: {results['papers_per_second']:.1f} papers/s")
    
    self.results["biorxiv"] = results
    return results
  
  def run_all_benchmarks(self) -> Dict:
    """Run complete benchmark suite.
    
    Returns:
      All benchmark results.
    """
    print("="*60)
    print("RUNNING COMPLETE PERFORMANCE BENCHMARK SUITE")
    print("="*60)
    
    test_queries = [
        "DNA methylation aging",
        "GDF-15 biomarker",
        "telomere length"
    ]
    
    self.benchmark_pubmed_search(test_queries)
    
    self.benchmark_abstract_fetching(pmid_count=20)
    
    self.benchmark_batch_processing(
        biomarker_terms=["Horvath clock", "GDF-15"],
        max_results=5
    )
    
    self.benchmark_rate_limiting()
    
    self.benchmark_biorxiv(keywords=["epigenetic clock"])
    
    print("\n" + "="*60)
    print("BENCHMARK SUITE COMPLETE")
    print("="*60)
    
    return self.results


def run_quick_benchmark(pubmed_email: str) -> None:
  """Run quick performance benchmark."""
  benchmark = PerformanceBenchmark(pubmed_email)
  results = benchmark.run_all_benchmarks()
  
  print("\n" + "="*60)
  print("PERFORMANCE SUMMARY")
  print("="*60)
  
  if "pubmed_search" in results:
    print(f"\nPubMed Search:")
    print(f"  {results['pubmed_search']['pmids_per_second']:.1f} PMIDs/s")
  
  if "abstract_fetching" in results:
    print(f"\nAbstract Fetching:")
    print(f"  {results['abstract_fetching']['papers_per_second']:.1f} papers/s")
  
  if "batch_processing" in results:
    print(f"\nBatch Processing:")
    print(f"  {results['batch_processing']['papers_per_second']:.1f} papers/s")
    print(f"  {results['batch_processing']['success_rate']:.1f}% success")


if __name__ == "__main__":
  run_quick_benchmark("biomarkerextract@test.com")
