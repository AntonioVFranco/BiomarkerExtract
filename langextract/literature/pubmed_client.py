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

"""PubMed API client using Biopython Entrez utilities."""

from __future__ import annotations

import time
from datetime import datetime
from typing import List, Optional

from Bio import Entrez


try:
  from langextract.literature import metadata_models as mm
except ImportError:
  import sys
  sys.path.append('..')
  from langextract.literature import metadata_models as mm


class PubMedClient:
  """Client for PubMed E-utilities API using Biopython."""
  
  def __init__(
      self,
      email: str,
      api_key: Optional[str] = None,
      tool: str = "BiomarkerExtract"
  ):
    """Initialize PubMed client with authentication.
    
    Args:
      email: Email address for NCBI identification.
      api_key: Optional API key for higher rate limits (10 req/s vs 3 req/s).
      tool: Tool name for NCBI tracking.
    """
    Entrez.email = email
    Entrez.tool = tool
    
    if api_key:
      Entrez.api_key = api_key
    
    self.email = email
    self.api_key = api_key
    self.requests_per_second = 10 if api_key else 3
    self.last_request_time = 0.0
  
  def _rate_limit(self) -> None:
    """Implement rate limiting for API requests."""
    min_interval = 1.0 / self.requests_per_second
    elapsed = time.time() - self.last_request_time
    
    if elapsed < min_interval:
      time.sleep(min_interval - elapsed)
    
    self.last_request_time = time.time()
  
  def search(
      self,
      query: str,
      max_results: int = 100,
      sort: str = "relevance",
      date_from: Optional[str] = None,
      date_to: Optional[str] = None
  ) -> List[str]:
    """Search PubMed and return list of PMIDs.
    
    Args:
      query: PubMed search query with field qualifiers.
      max_results: Maximum number of results to return.
      sort: Sort order: relevance, pub_date, or first_author.
      date_from: Start date in YYYY/MM/DD format.
      date_to: End date in YYYY/MM/DD format.
    
    Returns:
      List of PubMed IDs matching the query.
    """
    self._rate_limit()
    
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": sort
    }
    
    if date_from and date_to:
      search_params["mindate"] = date_from
      search_params["maxdate"] = date_to
      search_params["datetype"] = "pdat"
    
    handle = Entrez.esearch(**search_params)
    record = Entrez.read(handle)
    handle.close()
    
    return record.get("IdList", [])
  
  def fetch_abstracts(
      self,
      pmid_list: List[str],
      batch_size: int = 100
  ) -> List[mm.PaperMetadata]:
    """Fetch paper metadata including abstracts for list of PMIDs.
    
    Args:
      pmid_list: List of PubMed IDs to fetch.
      batch_size: Number of records to fetch per API call.
    
    Returns:
      List of PaperMetadata objects with parsed information.
    """
    papers = []
    
    for i in range(0, len(pmid_list), batch_size):
      batch = pmid_list[i:i + batch_size]
      self._rate_limit()
      
      handle = Entrez.efetch(
          db="pubmed",
          id=batch,
          rettype="medline",
          retmode="xml"
      )
      
      records = Entrez.read(handle)
      handle.close()
      
      for record in records['PubmedArticle']:
        paper = self._parse_pubmed_record(record)
        if paper:
          papers.append(paper)
    
    return papers
  
  def _parse_pubmed_record(self, record: dict) -> Optional[mm.PaperMetadata]:
    """Parse PubMed XML record into PaperMetadata object.
    
    Args:
      record: PubMed article record dictionary from Entrez.
    
    Returns:
      PaperMetadata object or None if parsing fails.
    """
    try:
      medline_citation = record['MedlineCitation']
      article = medline_citation['Article']
      
      pmid = str(medline_citation['PMID'])
      
      title = article.get('ArticleTitle', '')
      
      authors = []
      author_list = article.get('AuthorList', [])
      for author_data in author_list:
        if 'LastName' in author_data:
          author = mm.Author(
              last_name=author_data['LastName'],
              first_name=author_data.get('ForeName'),
              initials=author_data.get('Initials'),
              affiliation=author_data.get('Affiliation')
          )
          authors.append(author)
      
      abstract_parts = article.get('Abstract', {}).get('AbstractText', [])
      abstract = ' '.join(str(part) for part in abstract_parts)
      
      journal_info = article.get('Journal', {})
      journal = mm.Journal(
          name=journal_info.get('Title', ''),
          issn=journal_info.get('ISSN', ''),
          volume=journal_info.get('JournalIssue', {}).get('Volume'),
          issue=journal_info.get('JournalIssue', {}).get('Issue')
      )
      
      pub_date_info = journal_info.get('JournalIssue', {}).get('PubDate', {})
      pub_date = self._parse_publication_date(pub_date_info)
      
      mesh_terms = []
      mesh_heading_list = medline_citation.get('MeshHeadingList', [])
      for mesh_heading in mesh_heading_list:
        descriptor = mesh_heading.get('DescriptorName', {})
        if isinstance(descriptor, dict):
          mesh_terms.append(descriptor.get('$', ''))
        else:
          mesh_terms.append(str(descriptor))
      
      keywords = []
      keyword_list = medline_citation.get('KeywordList', [[]])[0]
      keywords = [str(kw) for kw in keyword_list]
      
      doi = None
      article_ids = record.get('PubmedData', {}).get('ArticleIdList', [])
      for article_id in article_ids:
        if article_id.attributes.get('IdType') == 'doi':
          doi = str(article_id)
      
      pub_type = self._determine_publication_type(article)
      
      return mm.PaperMetadata(
          pmid=pmid,
          doi=doi,
          title=title,
          authors=authors,
          journal=journal,
          publication_date=pub_date,
          publication_type=pub_type,
          source=mm.LiteratureSource.PUBMED,
          abstract=abstract if abstract else None,
          keywords=keywords,
          mesh_terms=mesh_terms,
          full_text_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
          metadata_extras={
              'pmcid': self._extract_pmcid(article_ids)
          }
      )
    
    except Exception as e:
      print(f"Error parsing PubMed record: {e}")
      return None
  
  def _parse_publication_date(self, pub_date_info: dict) -> Optional[datetime]:
    """Parse publication date from PubMed date structure."""
    try:
      year = int(pub_date_info.get('Year', 0))
      month = int(pub_date_info.get('Month', 1))
      day = int(pub_date_info.get('Day', 1))
      
      if year > 0:
        return datetime(year, month if month > 0 else 1, day if day > 0 else 1)
    except (ValueError, TypeError):
      pass
    
    return None
  
  def _determine_publication_type(self, article: dict) -> mm.PublicationType:
    """Determine publication type from article metadata."""
    pub_type_list = article.get('PublicationTypeList', [])
    
    for pub_type in pub_type_list:
      pub_type_str = str(pub_type).lower()
      
      if 'review' in pub_type_str:
        return mm.PublicationType.REVIEW
      elif 'meta-analysis' in pub_type_str:
        return mm.PublicationType.META_ANALYSIS
      elif 'clinical trial' in pub_type_str:
        return mm.PublicationType.CLINICAL_TRIAL
      elif 'case report' in pub_type_str:
        return mm.PublicationType.CASE_REPORT
    
    return mm.PublicationType.JOURNAL_ARTICLE
  
  def _extract_pmcid(self, article_ids: list) -> Optional[str]:
    """Extract PubMed Central ID if available."""
    for article_id in article_ids:
      if article_id.attributes.get('IdType') == 'pmc':
        return str(article_id)
    return None
  
  def search_biomarkers(
      self,
      biomarker_terms: List[str],
      aging_terms: List[str] = None,
      max_results: int = 100,
      years_back: int = 5
  ) -> List[mm.PaperMetadata]:
    """Convenience method for biomarker-specific searches.
    
    Args:
      biomarker_terms: List of biomarker-related terms.
      aging_terms: Optional list of aging-related terms.
      max_results: Maximum papers to return.
      years_back: How many years back to search.
    
    Returns:
      List of paper metadata objects.
    """
    if aging_terms is None:
      aging_terms = ["aging", "senescence", "longevity"]
    
    biomarker_query = " OR ".join(f'"{term}"[All Fields]' for term in biomarker_terms)
    aging_query = " OR ".join(f'"{term}"[MeSH Terms]' for term in aging_terms)
    
    current_year = datetime.now().year
    start_year = current_year - years_back
    
    query = f"({biomarker_query}) AND ({aging_query})"
    
    pmids = self.search(
        query=query,
        max_results=max_results,
        date_from=f"{start_year}/01/01",
        date_to=f"{current_year}/12/31"
    )
    
    return self.fetch_abstracts(pmids)
