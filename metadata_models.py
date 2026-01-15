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

"""Pydantic models for scientific literature metadata and content."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PublicationType(str, Enum):
  """Types of scientific publications."""
  
  JOURNAL_ARTICLE = "journal_article"
  PREPRINT = "preprint"
  REVIEW = "review"
  META_ANALYSIS = "meta_analysis"
  CLINICAL_TRIAL = "clinical_trial"
  CASE_REPORT = "case_report"


class LiteratureSource(str, Enum):
  """Source databases for literature retrieval."""
  
  PUBMED = "pubmed"
  BIORXIV = "biorxiv"
  MEDRXIV = "medrxiv"
  PMC = "pmc"
  GOOGLE_SCHOLAR = "google_scholar"


class Author(BaseModel):
  """Author information for scientific publications."""
  
  last_name: str = Field(..., min_length=1)
  first_name: Optional[str] = None
  initials: Optional[str] = None
  affiliation: Optional[str] = None
  orcid: Optional[str] = None
  
  @field_validator('orcid')
  @classmethod
  def validate_orcid_format(cls, v: Optional[str]) -> Optional[str]:
    """Validate ORCID identifier format."""
    if v and not v.startswith('0000-'):
      raise ValueError(f'ORCID must start with 0000-, got {v}')
    return v


class Journal(BaseModel):
  """Journal publication metadata."""
  
  name: str = Field(..., min_length=1)
  issn: Optional[str] = None
  volume: Optional[str] = None
  issue: Optional[str] = None
  pages: Optional[str] = None
  impact_factor: Optional[float] = Field(None, ge=0.0)


class PaperMetadata(BaseModel):
  """Complete metadata for a scientific paper."""
  
  pmid: Optional[str] = Field(
      None,
      description="PubMed identifier"
  )
  doi: Optional[str] = Field(
      None,
      description="Digital object identifier"
  )
  title: str = Field(
      ...,
      min_length=10,
      description="Paper title"
  )
  authors: List[Author] = Field(
      default_factory=list,
      description="List of paper authors"
  )
  journal: Optional[Journal] = Field(
      None,
      description="Journal information"
  )
  publication_date: Optional[datetime] = Field(
      None,
      description="Publication or preprint date"
  )
  publication_type: PublicationType = Field(
      ...,
      description="Type of publication"
  )
  source: LiteratureSource = Field(
      ...,
      description="Database source"
  )
  abstract: Optional[str] = Field(
      None,
      min_length=50,
      description="Paper abstract"
  )
  keywords: List[str] = Field(
      default_factory=list,
      description="Author-provided keywords"
  )
  mesh_terms: List[str] = Field(
      default_factory=list,
      description="Medical Subject Headings"
  )
  citation_count: int = Field(
      default=0,
      ge=0,
      description="Number of citations"
  )
  full_text_url: Optional[str] = None
  pdf_url: Optional[str] = None
  pdf_local_path: Optional[str] = None
  metadata_extras: Dict[str, Any] = Field(
      default_factory=dict,
      description="Additional source-specific metadata"
  )
  
  @field_validator('doi')
  @classmethod
  def validate_doi_format(cls, v: Optional[str]) -> Optional[str]:
    """Validate DOI format."""
    if v and not v.startswith('10.'):
      raise ValueError(f'DOI must start with 10., got {v}')
    return v
  
  def is_complete(self) -> bool:
    """Check if metadata has all critical fields."""
    return bool(
        self.title
        and self.authors
        and self.abstract
        and (self.pmid or self.doi)
    )


class PaperSection(BaseModel):
  """Extracted section from scientific paper."""
  
  section_type: str = Field(
      ...,
      description="Section name: abstract, methods, results, discussion"
  )
  content: str = Field(
      ...,
      min_length=10,
      description="Section text content"
  )
  page_numbers: List[int] = Field(
      default_factory=list,
      description="Pages where section appears"
  )
  subsections: List[PaperSection] = Field(
      default_factory=list,
      description="Nested subsections"
  )


class TableData(BaseModel):
  """Extracted table from scientific paper."""
  
  table_number: Optional[str] = None
  caption: Optional[str] = None
  headers: List[str] = Field(default_factory=list)
  rows: List[List[str]] = Field(default_factory=list)
  page_number: Optional[int] = None
  
  def to_markdown(self) -> str:
    """Convert table to markdown format."""
    if not self.headers or not self.rows:
      return ""
    
    lines = []
    if self.caption:
      lines.append(f"**{self.caption}**\n")
    
    lines.append("| " + " | ".join(self.headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(self.headers)) + " |")
    
    for row in self.rows:
      lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


class FigureData(BaseModel):
  """Extracted figure from scientific paper."""
  
  figure_number: Optional[str] = None
  caption: Optional[str] = None
  page_number: Optional[int] = None
  image_format: Optional[str] = None
  image_data: Optional[bytes] = Field(
      None,
      description="Binary image data",
      exclude=True
  )


class ParsedPaper(BaseModel):
  """Complete parsed paper with sections and extracted content."""
  
  metadata: PaperMetadata
  sections: List[PaperSection] = Field(default_factory=list)
  tables: List[TableData] = Field(default_factory=list)
  figures: List[FigureData] = Field(default_factory=list)
  references: List[str] = Field(default_factory=list)
  full_text: Optional[str] = None
  parsing_errors: List[str] = Field(default_factory=list)
  parsed_at: datetime = Field(default_factory=datetime.now)
  
  def get_section(self, section_type: str) -> Optional[PaperSection]:
    """Retrieve specific section by type."""
    for section in self.sections:
      if section.section_type.lower() == section_type.lower():
        return section
    return None
  
  def get_abstract(self) -> Optional[str]:
    """Get abstract text from metadata or sections."""
    if self.metadata.abstract:
      return self.metadata.abstract
    
    abstract_section = self.get_section('abstract')
    return abstract_section.content if abstract_section else None
  
  def get_results_section(self) -> Optional[str]:
    """Get results section text."""
    results = self.get_section('results')
    return results.content if results else None
  
  def get_methods_section(self) -> Optional[str]:
    """Get methods section text."""
    methods = self.get_section('methods')
    return methods.content if methods else None


class BatchProcessingResult(BaseModel):
  """Result of batch literature processing operation."""
  
  total_papers: int = Field(ge=0)
  successful: int = Field(ge=0)
  failed: int = Field(ge=0)
  papers: List[ParsedPaper] = Field(default_factory=list)
  errors: List[Dict[str, str]] = Field(default_factory=list)
  processing_time_seconds: float = Field(ge=0.0)
  
  def success_rate(self) -> float:
    """Calculate success rate percentage."""
    if self.total_papers == 0:
      return 0.0
    return (self.successful / self.total_papers) * 100.0
