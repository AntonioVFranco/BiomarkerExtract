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

"""Production pipeline with unified LLM provider support."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from tqdm import tqdm


try:
  from langextract.core import biomarker_models as bm
  from langextract.literature import batch_processor
  from langextract.providers import unified_llm_provider as ullm
except ImportError:
  import sys
  sys.path.append('..')
  from langextract.core import biomarker_models as bm
  from langextract.literature import batch_processor
  from langextract.providers import unified_llm_provider as ullm


class UnifiedProductionPipeline:
  """Complete production pipeline with all LLM providers."""
  
  def __init__(
      self,
      pubmed_email: str,
      llm_provider: str = "openrouter",
      llm_model: Optional[str] = None,
      llm_api_key: Optional[str] = None,
      pubmed_api_key: Optional[str] = None,
      output_dir: str = "pipeline_results"
  ):
    """Initialize production pipeline.
    
    Args:
      pubmed_email: Email for PubMed API.
      llm_provider: LLM provider (openrouter, openai, anthropic, gemini, ollama).
      llm_model: Model name. If None, uses latest default.
      llm_api_key: API key for LLM service.
      pubmed_api_key: Optional PubMed API key.
      output_dir: Directory for output files.
    """
    self.pubmed_email = pubmed_email
    self.pubmed_api_key = pubmed_api_key
    
    self.literature_processor = batch_processor.LiteratureBatchProcessor(
        pubmed_email=pubmed_email,
        pubmed_api_key=pubmed_api_key,
        max_workers=5
    )
    
    self.llm_provider = ullm.UnifiedLLMProvider(
        provider=llm_provider,
        model=llm_model,
        api_key=llm_api_key
    )
    
    self.output_dir = Path(output_dir)
    self.output_dir.mkdir(exist_ok=True)
    
    self.results = {
        "papers_processed": 0,
        "biomarkers_extracted": 0,
        "validated_biomarkers": 0,
        "high_confidence_biomarkers": 0,
        "categories": {}
    }
  
  def run_complete_pipeline(
      self,
      biomarker_terms: List[str],
      max_papers_per_term: int = 10,
      min_abstract_length: int = 100,
      extract_from_abstracts: bool = True
  ) -> Dict:
    """Run complete end-to-end pipeline.
    
    Args:
      biomarker_terms: List of biomarker search terms.
      max_papers_per_term: Max papers to retrieve per term.
      min_abstract_length: Minimum abstract length to process.
      extract_from_abstracts: Extract from abstracts vs full text.
    
    Returns:
      Pipeline results dictionary.
    """
    print("="*70)
    print("BIOMARKEREXTRACT UNIFIED PRODUCTION PIPELINE")
    print("="*70)
    print(f"LLM Provider: {self.llm_provider.provider}")
    print(f"LLM Model: {self.llm_provider.model_id}")
    print(f"Biomarker Terms: {len(biomarker_terms)}")
    print(f"Max Papers/Term: {max_papers_per_term}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    print("STEP 1: Literature Search")
    print("-" * 70)
    papers = self._search_literature(biomarker_terms, max_papers_per_term)
    print(f"✓ Found {len(papers)} papers")
    print()
    
    print("STEP 2: Filter and Prepare")
    print("-" * 70)
    valid_papers = self._filter_papers(papers, min_abstract_length)
    print(f"✓ {len(valid_papers)} papers with valid abstracts")
    print()
    
    print("STEP 3: Biomarker Extraction")
    print("-" * 70)
    extractions = self._extract_biomarkers(valid_papers, extract_from_abstracts)
    print(f"✓ Processed {len(extractions)} papers")
    print()
    
    print("STEP 4: Validation and Quality Assessment")
    print("-" * 70)
    validated = self._validate_and_assess(extractions)
    print(f"✓ Quality assessment complete")
    print()
    
    print("STEP 5: Export Results")
    print("-" * 70)
    export_files = self._export_results(validated, biomarker_terms)
    print(f"✓ Results exported to {len(export_files)} files")
    print()
    
    elapsed = time.time() - start_time
    
    self._print_final_summary(elapsed)
    
    return {
        "statistics": self.results,
        "export_files": export_files,
        "execution_time": elapsed
    }
  
  def _search_literature(
      self,
      terms: List[str],
      max_per_term: int
  ) -> List:
    """Search scientific literature."""
    result = self.literature_processor.search_biomarkers_comprehensive(
        biomarker_terms=terms,
        max_pubmed_results=max_per_term,
        preprint_days_back=90
    )
    
    self.results["papers_processed"] = len(result.papers)
    
    return result.papers
  
  def _filter_papers(
      self,
      papers: List,
      min_abstract_length: int
  ) -> List:
    """Filter papers with valid abstracts."""
    valid = []
    
    for paper in papers:
      if paper.metadata.abstract and len(paper.metadata.abstract) >= min_abstract_length:
        valid.append(paper)
    
    return valid
  
  def _extract_biomarkers(
      self,
      papers: List,
      from_abstracts: bool
  ) -> List[bm.BiomarkerExtraction]:
    """Extract biomarkers using LLM."""
    extractions = []
    
    for paper in tqdm(papers, desc="Extracting biomarkers"):
      try:
        text = paper.metadata.abstract if from_abstracts else paper.full_text
        
        if not text:
          continue
        
        extraction = self.llm_provider.extract_biomarkers(text)
        
        extraction.document_metadata.update({
            "pmid": paper.metadata.pmid,
            "doi": paper.metadata.doi,
            "title": paper.metadata.title,
            "source": paper.metadata.source.value
        })
        
        extractions.append(extraction)
        
        self.results["biomarkers_extracted"] += len(extraction.entities)
        
        time.sleep(0.5)
        
      except Exception as e:
        print(f"Error extracting from paper {paper.metadata.pmid}: {e}")
        continue
    
    return extractions
  
  def _validate_and_assess(
      self,
      extractions: List[bm.BiomarkerExtraction]
  ) -> List[bm.BiomarkerExtraction]:
    """Validate and assess biomarker quality."""
    for extraction in extractions:
      validated = extraction.get_validated_biomarkers()
      self.results["validated_biomarkers"] += len(validated)
      
      high_conf = extraction.get_high_confidence_entities(threshold=0.85)
      self.results["high_confidence_biomarkers"] += len(high_conf)
      
      for entity in extraction.entities:
        cat = entity.category.value
        self.results["categories"][cat] = self.results["categories"].get(cat, 0) + 1
    
    return extractions
  
  def _export_results(
      self,
      extractions: List[bm.BiomarkerExtraction],
      search_terms: List[str]
  ) -> List[Path]:
    """Export results to multiple formats."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    files = []
    
    all_biomarkers = []
    for extraction in extractions:
      for entity in extraction.entities:
        biomarker_dict = entity.model_dump()
        biomarker_dict["source_pmid"] = extraction.document_metadata.get("pmid")
        biomarker_dict["source_title"] = extraction.document_metadata.get("title")
        all_biomarkers.append(biomarker_dict)
    
    json_file = self.output_dir / f"biomarkers_{timestamp}.json"
    with open(json_file, 'w') as f:
      json.dump({
          "metadata": {
              "timestamp": datetime.now().isoformat(),
              "provider": self.llm_provider.provider,
              "model": self.llm_provider.model_id,
              "search_terms": search_terms,
              "statistics": self.results
          },
          "biomarkers": all_biomarkers
      }, f, indent=2, default=str)
    files.append(json_file)
    
    csv_file = self.output_dir / f"biomarkers_{timestamp}.csv"
    self._export_csv(all_biomarkers, csv_file)
    files.append(csv_file)
    
    summary_file = self.output_dir / f"summary_{timestamp}.txt"
    self._export_summary(summary_file)
    files.append(summary_file)
    
    return files
  
  def _export_csv(self, biomarkers: List[Dict], filepath: Path) -> None:
    """Export biomarkers to CSV."""
    import csv
    
    if not biomarkers:
      return
    
    fieldnames = [
        "name", "category", "measurement_method", "finding",
        "confidence", "source_pmid", "source_title"
    ]
    
    with open(filepath, 'w', newline='') as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
      writer.writeheader()
      writer.writerows(biomarkers)
  
  def _export_summary(self, filepath: Path) -> None:
    """Export summary statistics."""
    with open(filepath, 'w') as f:
      f.write("BIOMARKEREXTRACT PIPELINE SUMMARY\n")
      f.write("=" * 70 + "\n\n")
      f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
      f.write(f"LLM Provider: {self.llm_provider.provider}\n")
      f.write(f"LLM Model: {self.llm_provider.model_id}\n\n")
      f.write(f"Papers Processed: {self.results['papers_processed']}\n")
      f.write(f"Biomarkers Extracted: {self.results['biomarkers_extracted']}\n")
      f.write(f"Validated Biomarkers: {self.results['validated_biomarkers']}\n")
      f.write(f"High Confidence: {self.results['high_confidence_biomarkers']}\n\n")
      f.write("By Category:\n")
      for cat, count in sorted(self.results['categories'].items()):
        f.write(f"  {cat}: {count}\n")
  
  def _print_final_summary(self, elapsed: float) -> None:
    """Print final pipeline summary."""
    print("="*70)
    print("PIPELINE SUMMARY")
    print("="*70)
    print(f"Papers Processed: {self.results['papers_processed']}")
    print(f"Biomarkers Extracted: {self.results['biomarkers_extracted']}")
    print(f"Validated: {self.results['validated_biomarkers']}")
    print(f"High Confidence: {self.results['high_confidence_biomarkers']}")
    print()
    print("By Category:")
    for cat, count in sorted(self.results['categories'].items()):
      print(f"  {cat}: {count}")
    print()
    print(f"Execution Time: {elapsed:.1f}s")
    print(f"Output Directory: {self.output_dir}")
    print()
    print("="*70)
    print("PIPELINE COMPLETE ✓")
    print("="*70)


def run_pipeline(
    biomarker_terms: List[str],
    pubmed_email: str,
    provider: str = "openrouter",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    max_papers: int = 10
) -> Dict:
  """Run complete production pipeline.
  
  Args:
    biomarker_terms: Biomarker search terms.
    pubmed_email: PubMed email.
    provider: LLM provider (openrouter, openai, anthropic, gemini, ollama).
    model: Model name. If None, uses latest default.
    api_key: LLM API key.
    max_papers: Max papers per term.
  
  Returns:
    Pipeline results.
  """
  pipeline = UnifiedProductionPipeline(
      pubmed_email=pubmed_email,
      llm_provider=provider,
      llm_model=model,
      llm_api_key=api_key
  )
  
  return pipeline.run_complete_pipeline(
      biomarker_terms=biomarker_terms,
      max_papers_per_term=max_papers
  )


if __name__ == "__main__":
  import argparse
  
  parser = argparse.ArgumentParser(description="BiomarkerExtract Unified Pipeline")
  parser.add_argument("--terms", nargs="+", required=True, help="Biomarker search terms")
  parser.add_argument("--email", required=True, help="PubMed email")
  parser.add_argument("--provider", default="openrouter", help="LLM provider")
  parser.add_argument("--model", help="LLM model (optional, uses latest default)")
  parser.add_argument("--api-key", help="LLM API key")
  parser.add_argument("--max-papers", type=int, default=10, help="Max papers per term")
  
  args = parser.parse_args()
  
  run_pipeline(
      biomarker_terms=args.terms,
      pubmed_email=args.email,
      provider=args.provider,
      model=args.model,
      api_key=args.api_key,
      max_papers=args.max_papers
  )
