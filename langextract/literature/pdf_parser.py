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

"""PDF parsing for scientific papers using PyMuPDF."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

import fitz


try:
  from langextract.literature import metadata_models as mm
except ImportError:
  import sys
  sys.path.append('..')
  from langextract.literature import metadata_models as mm


class PaperPDFParser:
  """Parser for extracting content from scientific paper PDFs."""
  
  SECTION_PATTERNS = {
      'abstract': r'(?i)^abstract\s*$',
      'introduction': r'(?i)^introduction\s*$',
      'methods': r'(?i)^(methods?|materials? and methods?)\s*$',
      'results': r'(?i)^results?\s*$',
      'discussion': r'(?i)^discussion\s*$',
      'conclusion': r'(?i)^conclusions?\s*$',
      'references': r'(?i)^references?\s*$'
  }
  
  def __init__(self):
    """Initialize PDF parser."""
    pass
  
  def parse_pdf(
      self,
      pdf_path: str,
      extract_tables: bool = True,
      extract_figures: bool = True
  ) -> mm.ParsedPaper:
    """Parse PDF and extract structured content.
    
    Args:
      pdf_path: Path to PDF file.
      extract_tables: Whether to extract tables.
      extract_figures: Whether to extract figures.
    
    Returns:
      ParsedPaper object with extracted content.
    """
    errors = []
    
    try:
      doc = fitz.open(pdf_path)
    except Exception as e:
      errors.append(f"Failed to open PDF: {e}")
      return mm.ParsedPaper(
          metadata=mm.PaperMetadata(
              title="Failed to parse",
              publication_type=mm.PublicationType.JOURNAL_ARTICLE,
              source=mm.LiteratureSource.PUBMED
          ),
          parsing_errors=errors
      )
    
    full_text = self._extract_full_text(doc)
    
    sections = self._detect_sections(full_text)
    
    tables = []
    if extract_tables:
      tables = self._extract_tables(doc)
    
    figures = []
    if extract_figures:
      figures = self._extract_figures(doc)
    
    references = self._extract_references(full_text)
    
    title = self._extract_title(doc)
    abstract = self._extract_abstract_from_text(full_text)
    
    metadata = mm.PaperMetadata(
        title=title or "Unknown title",
        abstract=abstract,
        publication_type=mm.PublicationType.JOURNAL_ARTICLE,
        source=mm.LiteratureSource.PUBMED,
        pdf_local_path=pdf_path
    )
    
    doc.close()
    
    return mm.ParsedPaper(
        metadata=metadata,
        sections=sections,
        tables=tables,
        figures=figures,
        references=references,
        full_text=full_text,
        parsing_errors=errors
    )
  
  def _extract_full_text(self, doc: fitz.Document) -> str:
    """Extract all text from PDF document.
    
    Args:
      doc: Opened PyMuPDF document.
    
    Returns:
      Full text content.
    """
    text_parts = []
    
    for page in doc:
      text = page.get_text()
      text_parts.append(text)
    
    return '\n'.join(text_parts)
  
  def _extract_title(self, doc: fitz.Document) -> Optional[str]:
    """Extract paper title from first page.
    
    Args:
      doc: Opened PyMuPDF document.
    
    Returns:
      Paper title or None.
    """
    if len(doc) == 0:
      return None
    
    first_page = doc[0]
    text = first_page.get_text()
    
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    if non_empty_lines:
      title_candidates = non_empty_lines[:5]
      
      for candidate in title_candidates:
        if len(candidate) > 20 and len(candidate) < 300:
          return candidate
    
    return None
  
  def _detect_sections(self, full_text: str) -> List[mm.PaperSection]:
    """Detect and extract paper sections.
    
    Args:
      full_text: Complete paper text.
    
    Returns:
      List of PaperSection objects.
    """
    sections = []
    lines = full_text.split('\n')
    
    current_section = None
    current_content = []
    
    for line in lines:
      line_stripped = line.strip()
      
      section_found = False
      for section_name, pattern in self.SECTION_PATTERNS.items():
        if re.match(pattern, line_stripped):
          if current_section:
            sections.append(mm.PaperSection(
                section_type=current_section,
                content='\n'.join(current_content).strip()
            ))
          
          current_section = section_name
          current_content = []
          section_found = True
          break
      
      if not section_found and current_section:
        current_content.append(line)
    
    if current_section and current_content:
      sections.append(mm.PaperSection(
          section_type=current_section,
          content='\n'.join(current_content).strip()
      ))
    
    return sections
  
  def _extract_abstract_from_text(self, full_text: str) -> Optional[str]:
    """Extract abstract from full text.
    
    Args:
      full_text: Complete paper text.
    
    Returns:
      Abstract text or None.
    """
    pattern = r'(?i)abstract\s*\n(.*?)(?=\n\s*(?:introduction|background|keywords))'
    
    match = re.search(pattern, full_text, re.DOTALL)
    if match:
      abstract = match.group(1).strip()
      if len(abstract) > 50:
        return abstract
    
    return None
  
  def _extract_tables(self, doc: fitz.Document) -> List[mm.TableData]:
    """Extract tables from PDF document.
    
    Args:
      doc: Opened PyMuPDF document.
    
    Returns:
      List of TableData objects.
    """
    tables = []
    
    for page_num, page in enumerate(doc):
      text = page.get_text()
      
      table_matches = re.finditer(
          r'Table\s+(\d+)[\.:]?\s*([^\n]+)',
          text,
          re.IGNORECASE
      )
      
      for match in table_matches:
        table_number = match.group(1)
        caption = match.group(2).strip()
        
        table = mm.TableData(
            table_number=table_number,
            caption=caption,
            page_number=page_num + 1
        )
        tables.append(table)
    
    return tables
  
  def _extract_figures(self, doc: fitz.Document) -> List[mm.FigureData]:
    """Extract figures from PDF document.
    
    Args:
      doc: Opened PyMuPDF document.
    
    Returns:
      List of FigureData objects.
    """
    figures = []
    
    for page_num, page in enumerate(doc):
      img_list = page.get_images()
      
      for img_index, img in enumerate(img_list):
        xref = img[0]
        
        try:
          base_image = doc.extract_image(xref)
          
          figure = mm.FigureData(
              figure_number=f"{page_num + 1}.{img_index + 1}",
              page_number=page_num + 1,
              image_format=base_image['ext'],
              image_data=base_image['image']
          )
          figures.append(figure)
        
        except Exception:
          continue
    
    return figures
  
  def _extract_references(self, full_text: str) -> List[str]:
    """Extract references from full text.
    
    Args:
      full_text: Complete paper text.
    
    Returns:
      List of reference strings.
    """
    pattern = r'(?i)references\s*\n(.*?)$'
    
    match = re.search(pattern, full_text, re.DOTALL)
    if not match:
      return []
    
    references_text = match.group(1)
    
    ref_lines = references_text.split('\n')
    references = []
    
    current_ref = []
    for line in ref_lines:
      line_stripped = line.strip()
      
      if re.match(r'^\[\d+\]|\d+\.', line_stripped):
        if current_ref:
          references.append(' '.join(current_ref))
        current_ref = [line_stripped]
      elif current_ref:
        current_ref.append(line_stripped)
    
    if current_ref:
      references.append(' '.join(current_ref))
    
    return references[:100]
  
  def extract_text_only(self, pdf_path: str) -> str:
    """Quick extraction of text content only.
    
    Args:
      pdf_path: Path to PDF file.
    
    Returns:
      Full text content.
    """
    try:
      doc = fitz.open(pdf_path)
      text = self._extract_full_text(doc)
      doc.close()
      return text
    except Exception as e:
      return f"Error extracting text: {e}"
