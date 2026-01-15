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

"""Unit tests for biomarker_models module."""

import pytest
from pydantic import ValidationError

from langextract.core import biomarker_models as bm


class TestStatistics:
  """Test suite for Statistics model."""
  
  def test_valid_statistics(self):
    """Test creation of valid statistics object."""
    stats = bm.Statistics(
        p_value=0.001,
        effect_size=0.85,
        confidence_interval_lower=1.5,
        confidence_interval_upper=2.5,
        sample_size=1200,
        correlation_coefficient=0.75
    )
    assert stats.p_value == 0.001
    assert stats.sample_size == 1200
  
  def test_p_value_validation_rejects_nonsignificant(self):
    """Test that p-values >= 0.05 are rejected."""
    with pytest.raises(ValidationError) as excinfo:
      bm.Statistics(p_value=0.10)
    assert 'p-value must be < 0.05' in str(excinfo.value)
  
  def test_p_value_validation_accepts_significant(self):
    """Test that p-values < 0.05 are accepted."""
    stats = bm.Statistics(p_value=0.001)
    assert stats.p_value == 0.001
  
  def test_confidence_interval_order_validation(self):
    """Test that CI lower bound must be less than upper bound."""
    with pytest.raises(ValidationError) as excinfo:
      bm.Statistics(
          confidence_interval_lower=2.5,
          confidence_interval_upper=1.5
      )
    assert 'lower bound must be less than upper bound' in str(excinfo.value)
  
  def test_correlation_coefficient_bounds(self):
    """Test correlation coefficient must be between -1 and 1."""
    with pytest.raises(ValidationError):
      bm.Statistics(correlation_coefficient=1.5)
    
    with pytest.raises(ValidationError):
      bm.Statistics(correlation_coefficient=-1.5)
    
    stats = bm.Statistics(correlation_coefficient=0.8)
    assert stats.correlation_coefficient == 0.8


class TestControlledTerms:
  """Test suite for ControlledTerms model."""
  
  def test_valid_controlled_terms(self):
    """Test creation of valid controlled terms."""
    terms = bm.ControlledTerms(
        go_terms=['GO:0006306', 'GO:0007568'],
        kegg_pathways=['hsa04141', 'hsa04210'],
        uniprot_ids=['Q99988', 'P04637'],
        mesh_terms=['D000375', 'D019175'],
        gene_symbols=['FOXO3', 'TP53']
    )
    assert len(terms.go_terms) == 2
    assert len(terms.kegg_pathways) == 2
  
  def test_go_term_format_validation(self):
    """Test GO term format validation."""
    with pytest.raises(ValidationError) as excinfo:
      bm.ControlledTerms(go_terms=['GO:123'])
    assert 'GO term must match format' in str(excinfo.value)
    
    with pytest.raises(ValidationError):
      bm.ControlledTerms(go_terms=['INVALID'])
  
  def test_kegg_pathway_format_validation(self):
    """Test KEGG pathway format validation."""
    with pytest.raises(ValidationError) as excinfo:
      bm.ControlledTerms(kegg_pathways=['invalid123'])
    assert 'KEGG pathway must start with hsa or mmu' in str(excinfo.value)
  
  def test_uniprot_id_length_validation(self):
    """Test UniProt ID length validation."""
    with pytest.raises(ValidationError) as excinfo:
      bm.ControlledTerms(uniprot_ids=['ABC'])
    assert 'UniProt ID must be 6-10 characters' in str(excinfo.value)
  
  def test_mesh_term_format_validation(self):
    """Test MeSH term format validation."""
    with pytest.raises(ValidationError) as excinfo:
      bm.ControlledTerms(mesh_terms=['INVALID'])
    assert 'MeSH term must match format' in str(excinfo.value)


class TestValidationStatus:
  """Test suite for ValidationStatus model."""
  
  def test_valid_validation_status(self):
    """Test creation of valid validation status."""
    status = bm.ValidationStatus(
        is_validated=True,
        validation_cohorts=['cohort1', 'cohort2'],
        validation_studies=['PMID12345', 'PMID67890'],
        replication_count=2,
        reproducibility_cv=0.08
    )
    assert status.is_validated
    assert status.replication_count == 2
  
  def test_reproducibility_cv_threshold(self):
    """Test reproducibility CV threshold validation."""
    with pytest.raises(ValidationError) as excinfo:
      bm.ValidationStatus(reproducibility_cv=0.15)
    assert 'Reproducibility CV should be < 10%' in str(excinfo.value)
  
  def test_reproducibility_cv_accepts_valid(self):
    """Test that CV < 0.10 is accepted."""
    status = bm.ValidationStatus(reproducibility_cv=0.05)
    assert status.reproducibility_cv == 0.05


class TestBiomarkerEntity:
  """Test suite for BiomarkerEntity model."""
  
  def test_valid_biomarker_entity(self):
    """Test creation of valid biomarker entity."""
    entity = bm.BiomarkerEntity(
        name='Horvath clock',
        category=bm.BiomarkerCategory.EPIGENETIC,
        measurement_method='DNA methylation array',
        finding='Age acceleration 2.1 years in treatment vs controls',
        tissue_source='multi-tissue',
        statistics=bm.Statistics(
            p_value=0.001,
            effect_size=0.85,
            sample_size=1200
        ),
        validation_status=bm.ValidationStatus(
            is_validated=True,
            replication_count=1
        ),
        controlled_terms=bm.ControlledTerms(
            go_terms=['GO:0006306'],
            mesh_terms=['D019175']
        ),
        source_span=(0, 285),
        confidence=0.95
    )
    assert entity.name == 'Horvath clock'
    assert entity.category == bm.BiomarkerCategory.EPIGENETIC
    assert entity.confidence == 0.95
  
  def test_confidence_threshold_validation(self):
    """Test confidence score threshold validation."""
    with pytest.raises(ValidationError) as excinfo:
      bm.BiomarkerEntity(
          name='Test',
          category=bm.BiomarkerCategory.PROTEOMIC,
          measurement_method='ELISA',
          finding='Test finding result',
          confidence=0.50
      )
    assert 'Confidence score should be >= 0.70' in str(excinfo.value)
  
  def test_calculate_validation_score_high_quality(self):
    """Test validation score calculation for high-quality biomarker."""
    entity = bm.BiomarkerEntity(
        name='GDF-15',
        category=bm.BiomarkerCategory.PROTEOMIC,
        measurement_method='ELISA',
        finding='Significantly elevated in aged population',
        statistics=bm.Statistics(
            p_value=0.0001,
            sample_size=1500
        ),
        validation_status=bm.ValidationStatus(
            is_validated=True,
            replication_count=3
        ),
        controlled_terms=bm.ControlledTerms(
            go_terms=['GO:0043065'],
            kegg_pathways=['hsa04060'],
            uniprot_ids=['Q99988']
        ),
        confidence=0.92
    )
    score = entity.calculate_validation_score()
    assert score >= 80
  
  def test_calculate_validation_score_low_quality(self):
    """Test validation score for low-quality biomarker."""
    entity = bm.BiomarkerEntity(
        name='Exploratory marker',
        category=bm.BiomarkerCategory.METABOLOMIC,
        measurement_method='LC-MS',
        finding='Trend toward difference',
        confidence=0.75
    )
    score = entity.calculate_validation_score()
    assert score < 50
  
  def test_minimum_field_lengths(self):
    """Test minimum length requirements for string fields."""
    with pytest.raises(ValidationError):
      bm.BiomarkerEntity(
          name='A',
          category=bm.BiomarkerCategory.GENOMIC,
          measurement_method='X',
          finding='Short',
          confidence=0.80
      )


class TestBiomarkerRelationship:
  """Test suite for BiomarkerRelationship model."""
  
  def test_valid_relationship(self):
    """Test creation of valid biomarker relationship."""
    relationship = bm.BiomarkerRelationship(
        subject='Horvath clock',
        predicate=bm.RelationType.MEASURES,
        object='biological age acceleration',
        context='epigenetic aging measurement',
        evidence_span=(0, 100),
        confidence=0.90,
        statistics=bm.Statistics(
            correlation_coefficient=0.85,
            p_value=0.001
        )
    )
    assert relationship.subject == 'Horvath clock'
    assert relationship.predicate == bm.RelationType.MEASURES
    assert relationship.confidence == 0.90
  
  def test_relationship_confidence_threshold(self):
    """Test relationship confidence threshold validation."""
    with pytest.raises(ValidationError) as excinfo:
      bm.BiomarkerRelationship(
          subject='Test',
          predicate=bm.RelationType.CORRELATES_WITH,
          object='Outcome',
          confidence=0.50
      )
    assert 'Relationship confidence should be >= 0.60' in str(excinfo.value)


class TestBiomarkerExtraction:
  """Test suite for BiomarkerExtraction model."""
  
  def test_valid_extraction(self):
    """Test creation of valid biomarker extraction result."""
    entity = bm.BiomarkerEntity(
        name='Test biomarker',
        category=bm.BiomarkerCategory.PROTEOMIC,
        measurement_method='ELISA',
        finding='Significant elevation in aged samples',
        confidence=0.88
    )
    
    relationship = bm.BiomarkerRelationship(
        subject='Test biomarker',
        predicate=bm.RelationType.PREDICTS,
        object='mortality',
        confidence=0.82
    )
    
    extraction = bm.BiomarkerExtraction(
        entities=[entity],
        relationships=[relationship],
        document_metadata={'pmid': '12345'},
        extraction_timestamp='2026-01-14T00:00:00Z',
        model_version='gemini-2.5-flash'
    )
    
    assert len(extraction.entities) == 1
    assert len(extraction.relationships) == 1
  
  def test_get_validated_biomarkers(self):
    """Test filtering for validated biomarkers."""
    validated_entity = bm.BiomarkerEntity(
        name='Validated marker',
        category=bm.BiomarkerCategory.EPIGENETIC,
        measurement_method='Array',
        finding='Validated finding',
        validation_status=bm.ValidationStatus(is_validated=True),
        confidence=0.90
    )
    
    unvalidated_entity = bm.BiomarkerEntity(
        name='Exploratory marker',
        category=bm.BiomarkerCategory.METABOLOMIC,
        measurement_method='MS',
        finding='Exploratory finding',
        confidence=0.75
    )
    
    extraction = bm.BiomarkerExtraction(
        entities=[validated_entity, unvalidated_entity]
    )
    
    validated = extraction.get_validated_biomarkers()
    assert len(validated) == 1
    assert validated[0].name == 'Validated marker'
  
  def test_get_high_confidence_entities(self):
    """Test filtering for high-confidence entities."""
    high_conf_entity = bm.BiomarkerEntity(
        name='High confidence',
        category=bm.BiomarkerCategory.GENOMIC,
        measurement_method='qPCR',
        finding='Strong evidence',
        confidence=0.92
    )
    
    low_conf_entity = bm.BiomarkerEntity(
        name='Low confidence',
        category=bm.BiomarkerCategory.CELLULAR,
        measurement_method='Flow cytometry',
        finding='Weak evidence',
        confidence=0.75
    )
    
    extraction = bm.BiomarkerExtraction(
        entities=[high_conf_entity, low_conf_entity]
    )
    
    high_conf = extraction.get_high_confidence_entities(threshold=0.85)
    assert len(high_conf) == 1
    assert high_conf[0].name == 'High confidence'
  
  def test_calculate_overall_quality(self):
    """Test overall quality score calculation."""
    entity1 = bm.BiomarkerEntity(
        name='High quality',
        category=bm.BiomarkerCategory.PROTEOMIC,
        measurement_method='ELISA',
        finding='Well validated',
        statistics=bm.Statistics(p_value=0.0001, sample_size=1200),
        validation_status=bm.ValidationStatus(is_validated=True),
        confidence=0.95
    )
    
    entity2 = bm.BiomarkerEntity(
        name='Medium quality',
        category=bm.BiomarkerCategory.METABOLOMIC,
        measurement_method='LC-MS',
        finding='Partially validated',
        statistics=bm.Statistics(p_value=0.01, sample_size=300),
        confidence=0.80
    )
    
    extraction = bm.BiomarkerExtraction(entities=[entity1, entity2])
    
    quality = extraction.calculate_overall_quality()
    assert 0.0 <= quality <= 1.0
    assert quality > 0.5
  
  def test_empty_extraction_quality(self):
    """Test quality score for empty extraction."""
    extraction = bm.BiomarkerExtraction(entities=[])
    quality = extraction.calculate_overall_quality()
    assert quality == 0.0


class TestAssociation:
  """Test suite for Association model."""
  
  def test_valid_association(self):
    """Test creation of valid association."""
    assoc = bm.Association(
        phenotype='handgrip strength',
        association_type='correlation',
        effect_measure='correlation_coefficient',
        effect_value=-0.68,
        statistics=bm.Statistics(
            correlation_coefficient=-0.68,
            p_value=0.001
        )
    )
    assert assoc.phenotype == 'handgrip strength'
    assert assoc.effect_value == -0.68


if __name__ == '__main__':
  pytest.main([__file__, '-v'])
