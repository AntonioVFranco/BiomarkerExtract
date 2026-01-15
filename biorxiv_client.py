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

"""Client for bioRxiv and medRxiv preprint servers."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import List, Optional

import requests


try:
  from langextract.literature import metadata_models as mm
except ImportError:
  import sys
  sys.path.append('..')
  from langextract.literature import metadata_models as mm


class BioRxivClient:
  """Client for bioRxiv and medRxiv APIs."""
  
  BASE_URL = "https://api.biorxiv.org"
  
  def __init__(self, requests_per_minute: int = 60):
    """Initialize bioRxiv/medRxiv client.
    
    Args:
      requests_per_minute: Rate limit for API requests.
    """
    self.requests_per_minute = requests_per_minute
    self.last_request_time = 0.0
    self.session = requests.Session()
  
  def _rate_limit(self) -> None:
    """Implement rate limiting for API requests."""
    min_interval = 60.0 / self.requests_per_minute
    elapsed = time.time() - self.last_request_time
    
    if elapsed < min_interval:
      time.sleep(min_interval - elapsed)
    
    self.last_request_time = time.time()
  
  def fetch_papers(
      self,
      start_date: str,
      end_date: str,
      server: str = "biorxiv"
  ) -> List[dict]:
    """Fetch papers from bioRxiv or medRxiv for date range.
    
    Args:
      start_date: Start date in YYYY-MM-DD format.
      end_date: End date in YYYY-MM-DD format.
      server: Server name: 'biorxiv' or 'medrxiv'.
    
    Returns:
      List of paper dictionaries from API.
    """
    self._rate_limit()
    
    url = f"{self.BASE_URL}/details/{server}/{start_date}/{end_date}"
    
    response = self.session.get(url, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    return data.get('collection', [])
  
  def fetch_recent_papers(
      self,
      days_back: int = 30,
      server: str = "biorxiv"
  ) -> List[dict]:
    """Fetch papers from recent time period.
    
    Args:
      days_back: Number of days to look back.
      server: Server name: 'biorxiv' or 'medrxiv'.
    
    Returns:
      List of paper dictionaries.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return self.fetch_papers(
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        server=server
    )
  
  def search_by_keyword(
      self,
      keyword: str,
      days_back: int = 30,
      server: str = "biorxiv"
  ) -> List[mm.PaperMetadata]:
    """Search preprints by keyword in title or abstract.
    
    Args:
      keyword: Search keyword.
      days_back: Number of days to search back.
      server: Server name: 'biorxiv' or 'medrxiv'.
    
    Returns:
      List of PaperMetadata objects matching keyword.
    """
    papers_data = self.fetch_recent_papers(days_back, server)
    
    matching_papers = []
    keyword_lower = keyword.lower()
    
    for paper_data in papers_data:
      title = paper_data.get('title', '').lower()
      abstract = paper_data.get('abstract', '').lower()
      
      if keyword_lower in title or keyword_lower in abstract:
        paper = self._parse_preprint(paper_data, server)
        if paper:
          matching_papers.append(paper)
    
    return matching_papers
  
  def search_biomarkers(
      self,
      biomarker_terms: List[str],
      days_back: int = 90,
      server: str = "biorxiv"
  ) -> List[mm.PaperMetadata]:
    """Search for biomarker-related preprints.
    
    Args:
      biomarker_terms: List of biomarker terms to search.
      days_back: Number of days to search back.
      server: Server name.
    
    Returns:
      List of matching papers.
    """
    all_papers = []
    
    for term in biomarker_terms:
      papers = self.search_by_keyword(term, days_back, server)
      all_papers.extend(papers)
    
    seen_dois = set()
    unique_papers = []
    
    for paper in all_papers:
      if paper.doi and paper.doi not in seen_dois:
        seen_dois.add(paper.doi)
        unique_papers.append(paper)
    
    return unique_papers
  
  def _parse_preprint(
      self,
      paper_data: dict,
      server: str
  ) -> Optional[mm.PaperMetadata]:
    """Parse preprint data into PaperMetadata object.
    
    Args:
      paper_data: Raw paper data from API.
      server: Server name for source tracking.
    
    Returns:
      PaperMetadata object or None if parsing fails.
    """
    try:
      doi = paper_data.get('doi')
      if not doi:
        return None
      
      title = paper_data.get('title', '')
      if not title:
        return None
      
      authors = []
      authors_str = paper_data.get('authors', '')
      if authors_str:
        for author_name in authors_str.split(';'):
          author_name = author_name.strip()
          if author_name:
            parts = author_name.split(',')
            if len(parts) >= 1:
              author = mm.Author(
                  last_name=parts[0].strip(),
                  first_name=parts[1].strip() if len(parts) > 1 else None
              )
              authors.append(author)
      
      abstract = paper_data.get('abstract', '')
      
      date_str = paper_data.get('date', '')
      pub_date = None
      if date_str:
        try:
          pub_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
          pass
      
      category = paper_data.get('category', '')
      
      pdf_url = f"https://www.{server}.org/content/{doi}v{paper_data.get('version', '1')}.full.pdf"
      
      source = mm.LiteratureSource.BIORXIV if server == "biorxiv" else mm.LiteratureSource.MEDRXIV
      
      return mm.PaperMetadata(
          doi=doi,
          title=title,
          authors=authors,
          publication_date=pub_date,
          publication_type=mm.PublicationType.PREPRINT,
          source=source,
          abstract=abstract if abstract else None,
          pdf_url=pdf_url,
          full_text_url=f"https://www.{server}.org/content/{doi}",
          metadata_extras={
              'version': paper_data.get('version'),
              'category': category,
              'server': server
          }
      )
    
    except Exception as e:
      print(f"Error parsing preprint: {e}")
      return None
  
  def fetch_both_servers(
      self,
      keyword: str,
      days_back: int = 30
  ) -> List[mm.PaperMetadata]:
    """Search both bioRxiv and medRxiv for keyword.
    
    Args:
      keyword: Search keyword.
      days_back: Number of days to search.
    
    Returns:
      Combined list from both servers.
    """
    biorxiv_papers = self.search_by_keyword(keyword, days_back, "biorxiv")
    medrxiv_papers = self.search_by_keyword(keyword, days_back, "medrxiv")
    
    return biorxiv_papers + medrxiv_papers
