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

"""Batch processing for literature pipeline with parallel execution."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional

from tqdm import tqdm


try:
  from langextract.literature import metadata_models as mm
  from langextract.literature import pdf_parser
  from langextract.literature import pubmed_client
  from langextract.literature import biorxiv_client
except ImportError:
  import sys
  sys.path.append('..')
  from langextract.literature import metadata_models as mm
  from langextract.literature import pdf_parser
  from langextract.literature import pubmed_client
  from langextract.literature import biorxiv_client


class LiteratureBatchProcessor:
  """Batch processor for parallel literature retrieval and parsing."""
  
  def __init__(
      self,
      pubmed_email: str,
      pubmed_api_key: Optional[str] = None,
      max_workers: int = 10
  ):
    """Initialize batch processor.
    
    Args:
      pubmed_email: Email for PubMed API.
      pubmed_api_key: Optional API key for higher rate limits.
      max_workers: Maximum parallel workers.
    """
    self.pubmed_client = pubmed_client.PubMedClient(
        email=pubmed_email,
        api_key=pubmed_api_key
    )
    self.biorxiv_client = biorxiv_client.BioRxivClient()
    self.pdf_parser = pdf_parser.PaperPDFParser()
    self.max_workers = max_workers
  
  def process_pmids(
      self,
      pmid_list: List[str],
      fetch_abstracts: bool = True
  ) -> mm.BatchProcessingResult:
    """Process list of PubMed IDs in parallel.
    
    Args:
      pmid_list: List of PMIDs to process.
      fetch_abstracts: Whether to fetch full abstracts.
    
    Returns:
      BatchProcessingResult with papers and statistics.
    """
    start_time = time.time()
    
    papers = []
    errors = []
    
    if fetch_abstracts:
      try:
        papers = self.pubmed_client.fetch_abstracts(pmid_list)
      except Exception as e:
        errors.append({"error": str(e), "context": "fetch_abstracts"})
    
    processing_time = time.time() - start_time
    
    return mm.BatchProcessingResult(
        total_papers=len(pmid_list),
        successful=len(papers),
        failed=len(pmid_list) - len(papers),
        papers=[
            mm.ParsedPaper(metadata=paper) for paper in papers
        ],
        errors=errors,
        processing_time_seconds=processing_time
    )
  
  def process_pdfs(
      self,
      pdf_paths: List[str],
      show_progress: bool = True
  ) -> mm.BatchProcessingResult:
    """Process list of PDF files in parallel.
    
    Args:
      pdf_paths: List of paths to PDF files.
      show_progress: Whether to show progress bar.
    
    Returns:
      BatchProcessingResult with parsed papers.
    """
    start_time = time.time()
    
    papers = []
    errors = []
    
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
      futures = {
          executor.submit(self.pdf_parser.parse_pdf, path): path
          for path in pdf_paths
      }
      
      iterator = as_completed(futures)
      if show_progress:
        iterator = tqdm(iterator, total=len(pdf_paths), desc="Processing PDFs")
      
      for future in iterator:
        pdf_path = futures[future]
        try:
          paper = future.result()
          papers.append(paper)
        except Exception as e:
          errors.append({
              "pdf_path": pdf_path,
              "error": str(e)
          })
    
    processing_time = time.time() - start_time
    
    return mm.BatchProcessingResult(
        total_papers=len(pdf_paths),
        successful=len(papers),
        failed=len(errors),
        papers=papers,
        errors=errors,
        processing_time_seconds=processing_time
    )
  
  def search_and_retrieve(
      self,
      query: str,
      max_results: int = 100,
      include_preprints: bool = True,
      days_back: int = 30
  ) -> mm.BatchProcessingResult:
    """Search PubMed and optionally bioRxiv, retrieve all papers.
    
    Args:
      query: Search query string.
      max_results: Maximum results from PubMed.
      include_preprints: Whether to include bioRxiv/medRxiv.
      days_back: Days to search back for preprints.
    
    Returns:
      BatchProcessingResult with all retrieved papers.
    """
    start_time = time.time()
    
    papers = []
    errors = []
    
    try:
      pmids = self.pubmed_client.search(query, max_results=max_results)
      pubmed_papers = self.pubmed_client.fetch_abstracts(pmids)
      papers.extend([
          mm.ParsedPaper(metadata=paper) for paper in pubmed_papers
      ])
    except Exception as e:
      errors.append({"source": "pubmed", "error": str(e)})
    
    if include_preprints:
      try:
        preprints = self.biorxiv_client.fetch_both_servers(
            keyword=query,
            days_back=days_back
        )
        papers.extend([
            mm.ParsedPaper(metadata=paper) for paper in preprints
        ])
      except Exception as e:
        errors.append({"source": "preprints", "error": str(e)})
    
    processing_time = time.time() - start_time
    
    total_requested = max_results + (100 if include_preprints else 0)
    
    return mm.BatchProcessingResult(
        total_papers=total_requested,
        successful=len(papers),
        failed=len(errors),
        papers=papers,
        errors=errors,
        processing_time_seconds=processing_time
    )
  
  def process_custom_batch(
      self,
      items: List[any],
      process_func: Callable,
      show_progress: bool = True,
      description: str = "Processing"
  ) -> mm.BatchProcessingResult:
    """Process custom batch with user-defined function.
    
    Args:
      items: List of items to process.
      process_func: Function to apply to each item.
      show_progress: Whether to show progress bar.
      description: Description for progress bar.
    
    Returns:
      BatchProcessingResult with results.
    """
    start_time = time.time()
    
    results = []
    errors = []
    
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
      futures = {executor.submit(process_func, item): item for item in items}
      
      iterator = as_completed(futures)
      if show_progress:
        iterator = tqdm(iterator, total=len(items), desc=description)
      
      for future in iterator:
        item = futures[future]
        try:
          result = future.result()
          results.append(result)
        except Exception as e:
          errors.append({
              "item": str(item),
              "error": str(e)
          })
    
    processing_time = time.time() - start_time
    
    return mm.BatchProcessingResult(
        total_papers=len(items),
        successful=len(results),
        failed=len(errors),
        papers=results if results and isinstance(results[0], mm.ParsedPaper) else [],
        errors=errors,
        processing_time_seconds=processing_time
    )
  
  def search_biomarkers_comprehensive(
      self,
      biomarker_terms: List[str],
      max_pubmed_results: int = 100,
      preprint_days_back: int = 90
  ) -> mm.BatchProcessingResult:
    """Comprehensive biomarker search across all sources.
    
    Args:
      biomarker_terms: List of biomarker terms to search.
      max_pubmed_results: Max results from PubMed per term.
      preprint_days_back: Days to search preprints.
    
    Returns:
      BatchProcessingResult with all found papers.
    """
    start_time = time.time()
    
    all_papers = []
    errors = []
    
    for term in biomarker_terms:
      try:
        pubmed_papers = self.pubmed_client.search_biomarkers(
            biomarker_terms=[term],
            max_results=max_pubmed_results
        )
        all_papers.extend([
            mm.ParsedPaper(metadata=paper) for paper in pubmed_papers
        ])
      except Exception as e:
        errors.append({
            "term": term,
            "source": "pubmed",
            "error": str(e)
        })
      
      try:
        preprints = self.biorxiv_client.search_biomarkers(
            biomarker_terms=[term],
            days_back=preprint_days_back
        )
        all_papers.extend([
            mm.ParsedPaper(metadata=paper) for paper in preprints
        ])
      except Exception as e:
        errors.append({
            "term": term,
            "source": "preprints",
            "error": str(e)
        })
    
    seen_ids = set()
    unique_papers = []
    for paper in all_papers:
      paper_id = paper.metadata.pmid or paper.metadata.doi
      if paper_id and paper_id not in seen_ids:
        seen_ids.add(paper_id)
        unique_papers.append(paper)
    
    processing_time = time.time() - start_time
    
    return mm.BatchProcessingResult(
        total_papers=len(all_papers),
        successful=len(unique_papers),
        failed=len(errors),
        papers=unique_papers,
        errors=errors,
        processing_time_seconds=processing_time
    )
