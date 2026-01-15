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

"""Pydantic models for aging biomarker extraction with scientific validation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator


class BiomarkerCategory(str, Enum):
  """Biomarker categories based on omics layer and measurement approach."""
  
  EPIGENETIC = "epigenetic"
  PROTEOMIC = "proteomic"
  METABOLOMIC = "metabolomic"
  GENOMIC = "genomic"
  TRANSCRIPTOMIC = "transcriptomic"
  CELLULAR = "cellular"
  MULTI_OMICS = "multi_omics"


class Statistics(BaseModel):
  """Statistical measures for biomarker findings with validation rules."""
  
  p_value: Optional[float] = Field(
      None,
      ge=0.0,
      le=1.0,
      description="Statistical significance threshold"
  )
  effect_size: Optional[float] = Field(
      None,
      description="Cohen d, odds ratio, hazard ratio, or fold change"
  )
  confidence_interval_lower: Optional[float] = Field(
      None,
      description="Lower bound of 95% CI"
  )
  confidence_interval_upper: Optional[float] = Field(
      None,
      description="Upper bound of 95% CI"
  )
  sample_size: Optional[int] = Field(
      None,
      ge=1,
      description="Number of samples in study"
  )
  test_statistic: Optional[float] = Field(
      None,
      description="t-statistic, z-score, or F-statistic"
  )
  correlation_coefficient: Optional[float] = Field(
      None,
      ge=-1.0,
      le=1.0,
      description="Pearson or Spearman correlation"
  )
  
  @field_validator('p_value')
  @classmethod
  def validate_p_value_significance(cls, v: Optional[float]) -> Optional[float]:
    """Ensure p-value indicates statistical significance when provided."""
    if v is not None and v >= 0.05:
      raise ValueError(
          f'p-value must be < 0.05 for statistical significance, got {v}'
      )
    return v
  
  @model_validator(mode='after')
  def validate_confidence_interval_order(self) -> Statistics:
    """Ensure confidence interval lower bound is less than upper bound."""
    if (
        self.confidence_interval_lower is not None
        and self.confidence_interval_upper is not None
    ):
      if self.confidence_interval_lower >= self.confidence_interval_upper:
        raise ValueError(
            'Confidence interval lower bound must be less than upper bound'
        )
    return self


class ControlledTerms(BaseModel):
  """Controlled vocabulary mappings for biomarker entities."""
  
  go_terms: List[str] = Field(
      default_factory=list,
      description="Gene Ontology terms"
  )
  kegg_pathways: List[str] = Field(
      default_factory=list,
      description="KEGG pathway identifiers"
  )
  uniprot_ids: List[str] = Field(
      default_factory=list,
      description="UniProt protein identifiers"
  )
  mesh_terms: List[str] = Field(
      default_factory=list,
      description="Medical Subject Headings"
  )
  gene_symbols: List[str] = Field(
      default_factory=list,
      description="HGNC gene symbols"
  )
  
  @field_validator('go_terms')
  @classmethod
  def validate_go_format(cls, v: List[str]) -> List[str]:
    """Validate GO term format."""
    for term in v:
      if not term.startswith('GO:') or len(term) != 10:
        raise ValueError(
            f'GO term must match format GO:XXXXXXX, got {term}'
        )
    return v
  
  @field_validator('kegg_pathways')
  @classmethod
  def validate_kegg_format(cls, v: List[str]) -> List[str]:
    """Validate KEGG pathway format."""
    for pathway in v:
      if not pathway.startswith('hsa') and not pathway.startswith('mmu'):
        raise ValueError(
            f'KEGG pathway must start with hsa or mmu, got {pathway}'
        )
    return v
  
  @field_validator('uniprot_ids')
  @classmethod
  def validate_uniprot_format(cls, v: List[str]) -> List[str]:
    """Validate UniProt ID format."""
    for uniprot_id in v:
      if len(uniprot_id) < 6 or len(uniprot_id) > 10:
        raise ValueError(
            f'UniProt ID must be 6-10 characters, got {uniprot_id}'
        )
    return v
  
  @field_validator('mesh_terms')
  @classmethod
  def validate_mesh_format(cls, v: List[str]) -> List[str]:
    """Validate MeSH term format."""
    for term in v:
      if not term.startswith('D') or not term[1:].isdigit():
        raise ValueError(
            f'MeSH term must match format DXXXXXX, got {term}'
        )
    return v


class ValidationStatus(BaseModel):
  """Biomarker validation information across cohorts and studies."""
  
  is_validated: bool = Field(
      default=False,
      description="Whether biomarker is validated across multiple cohorts"
  )
  validation_cohorts: List[str] = Field(
      default_factory=list,
      description="Names or identifiers of validation cohorts"
  )
  validation_studies: List[str] = Field(
      default_factory=list,
      description="PMIDs or DOIs of validation studies"
  )
  replication_count: int = Field(
      default=0,
      ge=0,
      description="Number of independent replications"
  )
  reproducibility_cv: Optional[float] = Field(
      None,
      ge=0.0,
      le=1.0,
      description="Coefficient of variation for reproducibility"
  )
  
  @field_validator('reproducibility_cv')
  @classmethod
  def validate_reproducibility_threshold(
      cls,
      v: Optional[float]
  ) -> Optional[float]:
    """Ensure reproducibility meets quality threshold."""
    if v is not None and v > 0.10:
      raise ValueError(
          f'Reproducibility CV should be < 10% for validated biomarkers, got {v*100}%'
      )
    return v


class Association(BaseModel):
  """Association between biomarker and phenotype or outcome."""
  
  phenotype: str = Field(
      ...,
      description="Associated phenotype or outcome"
  )
  association_type: str = Field(
      ...,
      description="Type of association: correlation, prediction, causation"
  )
  effect_measure: Optional[str] = Field(
      None,
      description="Measure type: hazard ratio, odds ratio, correlation"
  )
  effect_value: Optional[float] = Field(
      None,
      description="Numerical value of association"
  )
  statistics: Optional[Statistics] = Field(
      None,
      description="Statistical support for association"
  )


class BiomarkerEntity(BaseModel):
  """Complete biomarker entity with metadata and validation."""
  
  name: str = Field(
      ...,
      min_length=2,
      description="Biomarker name or identifier"
  )
  category: BiomarkerCategory = Field(
      ...,
      description="Biomarker category by omics layer"
  )
  measurement_method: str = Field(
      ...,
      min_length=2,
      description="Laboratory technique or assay used"
  )
  finding: str = Field(
      ...,
      min_length=10,
      description="Quantitative or qualitative finding description"
  )
  tissue_source: Optional[str] = Field(
      None,
      description="Biological tissue or fluid source"
  )
  statistics: Optional[Statistics] = Field(
      None,
      description="Statistical measures supporting finding"
  )
  validation_status: Optional[ValidationStatus] = Field(
      None,
      description="Validation across cohorts and studies"
  )
  controlled_terms: ControlledTerms = Field(
      default_factory=ControlledTerms,
      description="Ontology and vocabulary mappings"
  )
  associations: List[Association] = Field(
      default_factory=list,
      description="Phenotypic or clinical associations"
  )
  source_span: Optional[Tuple[int, int]] = Field(
      None,
      description="Character span in source text"
  )
  confidence: float = Field(
      ...,
      ge=0.0,
      le=1.0,
      description="Extraction confidence score"
  )
  metadata: Dict[str, Any] = Field(
      default_factory=dict,
      description="Additional metadata"
  )
  
  @field_validator('confidence')
  @classmethod
  def validate_confidence_threshold(cls, v: float) -> float:
    """Warn if confidence is below recommended threshold."""
    if v < 0.70:
      raise ValueError(
          f'Confidence score should be >= 0.70 for reliable extraction, got {v}'
      )
    return v
  
  def calculate_validation_score(self) -> int:
    """Calculate validation score based on quality criteria."""
    score = 0
    
    if self.validation_status and self.validation_status.is_validated:
      score += 20
    
    if self.statistics and self.statistics.p_value:
      if self.statistics.p_value < 0.001:
        score += 30
      elif self.statistics.p_value < 0.01:
        score += 20
      else:
        score += 10
    
    if self.statistics and self.statistics.sample_size:
      if self.statistics.sample_size > 1000:
        score += 20
      elif self.statistics.sample_size > 500:
        score += 15
      elif self.statistics.sample_size > 100:
        score += 10
    
    if self.controlled_terms:
      term_count = (
          len(self.controlled_terms.go_terms)
          + len(self.controlled_terms.kegg_pathways)
          + len(self.controlled_terms.uniprot_ids)
      )
      score += min(term_count * 5, 20)
    
    if (
        self.validation_status
        and self.validation_status.replication_count > 0
    ):
      score += min(self.validation_status.replication_count * 10, 30)
    
    return min(score, 100)


class RelationType(str, Enum):
  """Types of relationships between biomarker entities."""
  
  MEASURES = "measures"
  PREDICTS = "predicts"
  CORRELATES_WITH = "correlates_with"
  VALIDATED_BY = "validated_by"
  ASSOCIATED_WITH = "associated_with"
  INFLUENCES = "influences"
  DERIVED_FROM = "derived_from"


class BiomarkerRelationship(BaseModel):
  """Relationship between biomarker entities or concepts."""
  
  subject: str = Field(
      ...,
      description="Subject entity in relationship"
  )
  predicate: RelationType = Field(
      ...,
      description="Type of relationship"
  )
  object: str = Field(
      ...,
      description="Object entity in relationship"
  )
  context: Optional[str] = Field(
      None,
      description="Contextual information for relationship"
  )
  evidence_span: Optional[Tuple[int, int]] = Field(
      None,
      description="Character span of supporting evidence"
  )
  confidence: float = Field(
      ...,
      ge=0.0,
      le=1.0,
      description="Relationship confidence score"
  )
  statistics: Optional[Statistics] = Field(
      None,
      description="Statistical support for relationship"
  )
  
  @field_validator('confidence')
  @classmethod
  def validate_relationship_confidence(cls, v: float) -> float:
    """Ensure relationship confidence meets threshold."""
    if v < 0.60:
      raise ValueError(
          f'Relationship confidence should be >= 0.60, got {v}'
      )
    return v


class BiomarkerExtraction(BaseModel):
  """Complete extraction result with entities and relationships."""
  
  entities: List[BiomarkerEntity] = Field(
      default_factory=list,
      description="Extracted biomarker entities"
  )
  relationships: List[BiomarkerRelationship] = Field(
      default_factory=list,
      description="Relationships between entities"
  )
  document_metadata: Dict[str, Any] = Field(
      default_factory=dict,
      description="Source document metadata"
  )
  extraction_timestamp: Optional[str] = Field(
      None,
      description="ISO timestamp of extraction"
  )
  model_version: Optional[str] = Field(
      None,
      description="Model version used for extraction"
  )
  
  def get_validated_biomarkers(self) -> List[BiomarkerEntity]:
    """Return only validated biomarkers."""
    return [
        entity for entity in self.entities
        if entity.validation_status and entity.validation_status.is_validated
    ]
  
  def get_high_confidence_entities(
      self,
      threshold: float = 0.85
  ) -> List[BiomarkerEntity]:
    """Return biomarkers above confidence threshold."""
    return [
        entity for entity in self.entities
        if entity.confidence >= threshold
    ]
  
  def calculate_overall_quality(self) -> float:
    """Calculate overall extraction quality score."""
    if not self.entities:
      return 0.0
    
    validation_scores = [
        entity.calculate_validation_score() for entity in self.entities
    ]
    return sum(validation_scores) / len(validation_scores) / 100.0
