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

"""Gemini provider specialized for aging biomarker extraction."""

from __future__ import annotations

import dataclasses
from typing import Any, List, Optional

from langextract.providers import gemini


_BIOMARKER_SYSTEM_INSTRUCTION = """You are an expert in aging research and biomarker validation with deep knowledge of:
- Hallmarks of aging and associated molecular markers
- Epigenetic clocks (Horvath, Hannum, PhenoAge, GrimAge, DunedinPACE)
- Multi-omics biomarkers (genomic, epigenetic, transcriptomic, proteomic, metabolomic)
- Controlled vocabularies: Gene Ontology, KEGG pathways, UniProt, MeSH
- Statistical validation criteria for aging research

Your task is to extract biomarkers with scientific rigor."""


_BIOMARKER_EXTRACTION_PROMPT_TEMPLATE = """Extract aging biomarkers from the scientific text below.

EXTRACTION REQUIREMENTS:
1. Biomarker Identity:
   - Official or commonly used name
   - Category: epigenetic, proteomic, metabolomic, genomic, transcriptomic, cellular, or multi_omics
   - Measurement method and technical specifications

2. Quantitative Findings:
   - Numerical results with units
   - Statistical significance (p-value must be < 0.05)
   - Effect sizes, confidence intervals, sample sizes
   - Avoid qualitative-only findings

3. Validation Status:
   - Replication across cohorts
   - Independent validation studies
   - Number of replications
   - Validation cohort details

4. Controlled Vocabulary Mapping:
   - Gene Ontology (GO) terms for biological processes
   - KEGG pathways for molecular mechanisms
   - UniProt IDs for proteins
   - MeSH terms for medical concepts
   - HGNC gene symbols where applicable

5. Associations:
   - Link biomarkers to phenotypes or outcomes
   - Include correlation coefficients, hazard ratios, or odds ratios
   - Specify predictive relationships

QUALITY CRITERIA:
- Prioritize validated biomarkers over exploratory findings
- Include only statistically significant results (p < 0.05)
- Prefer quantitative findings with effect sizes
- Map to standard ontologies when possible
- Include confidence scores for extracted entities

CONTROLLED VOCABULARY FORMATS:
- GO terms: GO:XXXXXXX (7 digits)
- KEGG pathways: hsa##### or mmu##### (human or mouse)
- UniProt IDs: 6-10 alphanumeric characters
- MeSH terms: D###### (6 digits)

OUTPUT FORMAT:
Return structured data with exact text spans for provenance.

{few_shot_examples}

TEXT TO ANALYZE:
{input_text}
"""


_FEW_SHOT_EXAMPLE_1 = """
EXAMPLE 1 - EPIGENETIC CLOCK:

Input Text:
"DNA methylation age was assessed using the Horvath multi-tissue clock, which utilizes 353 CpG sites. In our cohort (n=1,200), biological age acceleration averaged 2.1 years (SD=4.2) in the intervention group compared to -1.3 years (SD=3.8) in controls (p<0.001, Cohen's d=0.85). This finding was replicated in an independent validation cohort (n=450)."

Expected Extraction:
{{
  "name": "Horvath clock",
  "category": "epigenetic",
  "measurement_method": "DNA methylation array",
  "finding": "Age acceleration 2.1 years in treatment vs -1.3 years in controls",
  "tissue_source": "multi-tissue",
  "statistics": {{
    "p_value": 0.001,
    "effect_size": 0.85,
    "sample_size": 1200
  }},
  "validation_status": {{
    "is_validated": true,
    "validation_cohorts": ["independent cohort"],
    "replication_count": 1
  }},
  "controlled_terms": {{
    "go_terms": ["GO:0006306"],
    "mesh_terms": ["D019175"]
  }},
  "source_span": [0, 285],
  "confidence": 0.95
}}
"""


_FEW_SHOT_EXAMPLE_2 = """
EXAMPLE 2 - PROTEOMIC BIOMARKER:

Input Text:
"Circulating GDF-15 levels were quantified by ELISA. Baseline GDF-15 was significantly higher in the aged group (median 850 pg/mL, IQR 720-1020) versus young controls (median 320 pg/mL, IQR 280-380, p<0.0001). GDF-15 correlated strongly with handgrip strength (r=-0.68, p<0.001) and predicted 5-year mortality (HR=1.42 per log unit, 95% CI 1.28-1.58, p<0.0001)."

Expected Extraction:
{{
  "name": "GDF-15",
  "category": "proteomic",
  "measurement_method": "ELISA",
  "finding": "Median 850 pg/mL in aged vs 320 pg/mL in young",
  "tissue_source": "plasma",
  "statistics": {{
    "p_value": 0.0001,
    "effect_size": 2.66
  }},
  "controlled_terms": {{
    "uniprot_ids": ["Q99988"],
    "go_terms": ["GO:0043065"],
    "kegg_pathways": ["hsa04060"]
  }},
  "associations": [
    {{
      "phenotype": "handgrip strength",
      "association_type": "correlation",
      "effect_measure": "correlation",
      "effect_value": -0.68,
      "statistics": {{"p_value": 0.001}}
    }},
    {{
      "phenotype": "5-year mortality",
      "association_type": "prediction",
      "effect_measure": "hazard_ratio",
      "effect_value": 1.42,
      "statistics": {{
        "p_value": 0.0001,
        "confidence_interval_lower": 1.28,
        "confidence_interval_upper": 1.58
      }}
    }}
  ],
  "source_span": [0, 350],
  "confidence": 0.92
}}
"""


@dataclasses.dataclass(init=False)
class GeminiBiomarkerProvider(gemini.GeminiLanguageModel):
  """Gemini provider specialized for aging biomarker extraction.
  
  Extends the base Gemini provider with domain-specific prompts,
  few-shot examples, and validation logic for biomarker extraction.
  """
  
  def __init__(
      self,
      model_id: str = 'gemini-2.5-flash',
      api_key: Optional[str] = None,
      temperature: float = 0.0,
      include_few_shot: bool = True,
      **kwargs: Any
  ):
    """Initialize biomarker-specific Gemini provider.
    
    Args:
      model_id: Gemini model identifier.
      api_key: Google API key for authentication.
      temperature: Sampling temperature (0.0 for deterministic).
      include_few_shot: Whether to include few-shot examples.
      **kwargs: Additional arguments passed to base GeminiLanguageModel.
    """
    kwargs['system_instruction'] = _BIOMARKER_SYSTEM_INSTRUCTION
    
    super().__init__(
        model_id=model_id,
        api_key=api_key,
        temperature=temperature,
        **kwargs
    )
    
    self.include_few_shot = include_few_shot
  
  def create_biomarker_prompt(
      self,
      text: str,
      include_examples: Optional[bool] = None
  ) -> str:
    """Create biomarker extraction prompt with optional few-shot examples.
    
    Args:
      text: Input text to extract biomarkers from.
      include_examples: Override class-level few-shot setting.
    
    Returns:
      Formatted prompt string.
    """
    if include_examples is None:
      include_examples = self.include_few_shot
    
    if include_examples:
      few_shot_section = (
          "FEW-SHOT EXAMPLES:\n\n"
          + _FEW_SHOT_EXAMPLE_1
          + "\n\n"
          + _FEW_SHOT_EXAMPLE_2
      )
    else:
      few_shot_section = ""
    
    return _BIOMARKER_EXTRACTION_PROMPT_TEMPLATE.format(
        few_shot_examples=few_shot_section,
        input_text=text
    )
  
  def get_extraction_schema(self) -> dict[str, Any]:
    """Return JSON schema for biomarker extraction.
    
    Returns:
      Dictionary defining biomarker entity schema.
    """
    return {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "epigenetic",
                                "proteomic",
                                "metabolomic",
                                "genomic",
                                "transcriptomic",
                                "cellular",
                                "multi_omics"
                            ]
                        },
                        "measurement_method": {"type": "string"},
                        "finding": {"type": "string"},
                        "tissue_source": {"type": "string"},
                        "statistics": {
                            "type": "object",
                            "properties": {
                                "p_value": {"type": "number"},
                                "effect_size": {"type": "number"},
                                "confidence_interval_lower": {"type": "number"},
                                "confidence_interval_upper": {"type": "number"},
                                "sample_size": {"type": "integer"},
                                "correlation_coefficient": {"type": "number"}
                            }
                        },
                        "validation_status": {
                            "type": "object",
                            "properties": {
                                "is_validated": {"type": "boolean"},
                                "validation_cohorts": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "validation_studies": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "replication_count": {"type": "integer"}
                            }
                        },
                        "controlled_terms": {
                            "type": "object",
                            "properties": {
                                "go_terms": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "kegg_pathways": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "uniprot_ids": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "mesh_terms": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "gene_symbols": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        },
                        "associations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "phenotype": {"type": "string"},
                                    "association_type": {"type": "string"},
                                    "effect_measure": {"type": "string"},
                                    "effect_value": {"type": "number"}
                                }
                            }
                        },
                        "source_span": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "required": [
                        "name",
                        "category",
                        "measurement_method",
                        "finding",
                        "confidence"
                    ]
                }
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string"},
                        "predicate": {
                            "type": "string",
                            "enum": [
                                "measures",
                                "predicts",
                                "correlates_with",
                                "validated_by",
                                "associated_with",
                                "influences",
                                "derived_from"
                            ]
                        },
                        "object": {"type": "string"},
                        "confidence": {"type": "number"}
                    },
                    "required": ["subject", "predicate", "object", "confidence"]
                }
            }
        },
        "required": ["entities"]
    }
