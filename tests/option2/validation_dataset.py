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

"""Golden validation dataset of known aging biomarkers for accuracy testing."""

from __future__ import annotations

from typing import Dict, List

from langextract.core import biomarker_models as bm


GOLDEN_BIOMARKERS = [
    {
        "name": "Horvath Clock",
        "category": bm.BiomarkerCategory.EPIGENETIC,
        "measurement_method": "DNA methylation array",
        "key_features": ["353 CpG sites", "multi-tissue"],
        "expected_go_terms": ["GO:0006306"],
        "expected_genes": ["DNMT1", "DNMT3A", "DNMT3B"],
        "validation_studies": ["PMID:24138928"],
        "year_published": 2013,
        "search_queries": [
            "Horvath clock DNA methylation",
            "Horvath epigenetic age",
            "353 CpG sites aging"
        ]
    },
    {
        "name": "GrimAge",
        "category": bm.BiomarkerCategory.EPIGENETIC,
        "measurement_method": "DNA methylation array",
        "key_features": ["1030 CpG sites", "mortality prediction"],
        "expected_go_terms": ["GO:0006306"],
        "expected_genes": ["DNMT1"],
        "validation_studies": ["PMID:30669119"],
        "year_published": 2019,
        "search_queries": [
            "GrimAge mortality prediction",
            "GrimAge DNA methylation",
            "epigenetic mortality clock"
        ]
    },
    {
        "name": "DunedinPACE",
        "category": bm.BiomarkerCategory.EPIGENETIC,
        "measurement_method": "DNA methylation array",
        "key_features": ["pace of aging", "longitudinal"],
        "expected_go_terms": ["GO:0006306"],
        "validation_studies": ["PMID:35029144"],
        "year_published": 2022,
        "search_queries": [
            "DunedinPACE pace aging",
            "DunedinPACE DNA methylation",
            "pace of aging biomarker"
        ]
    },
    {
        "name": "PhenoAge",
        "category": bm.BiomarkerCategory.EPIGENETIC,
        "measurement_method": "DNA methylation array",
        "key_features": ["513 CpG sites", "phenotypic age"],
        "expected_go_terms": ["GO:0006306"],
        "validation_studies": ["PMID:29676998"],
        "year_published": 2018,
        "search_queries": [
            "PhenoAge phenotypic age",
            "PhenoAge DNA methylation",
            "phenotypic age biomarker"
        ]
    },
    {
        "name": "GDF-15",
        "category": bm.BiomarkerCategory.PROTEOMIC,
        "measurement_method": "ELISA",
        "key_features": ["mitochondrial stress", "mortality predictor"],
        "expected_go_terms": ["GO:0043065"],
        "expected_uniprot": ["Q99988"],
        "expected_kegg": ["hsa04060"],
        "validation_studies": ["PMID:28877457"],
        "year_published": 2017,
        "search_queries": [
            "GDF-15 aging biomarker",
            "growth differentiation factor 15 aging",
            "GDF-15 mitochondrial stress"
        ]
    },
    {
        "name": "NAD+/NADH Ratio",
        "category": bm.BiomarkerCategory.METABOLOMIC,
        "measurement_method": "LC-MS",
        "key_features": ["NAD+ decline", "metabolic health"],
        "expected_go_terms": ["GO:0019674"],
        "expected_kegg": ["hsa00760"],
        "validation_studies": ["PMID:27304511"],
        "year_published": 2016,
        "search_queries": [
            "NAD+ aging decline",
            "NAD NADH ratio aging",
            "nicotinamide adenine dinucleotide aging"
        ]
    },
    {
        "name": "Telomere Length",
        "category": bm.BiomarkerCategory.GENOMIC,
        "measurement_method": "qPCR",
        "key_features": ["chromosomal shortening", "replicative senescence"],
        "expected_go_terms": ["GO:0000723"],
        "expected_genes": ["TERT", "TERC"],
        "validation_studies": ["PMID:22582263"],
        "year_published": 2012,
        "search_queries": [
            "telomere length aging biomarker",
            "telomere attrition aging",
            "telomere shortening senescence"
        ]
    },
    {
        "name": "p16INK4a",
        "category": bm.BiomarkerCategory.CELLULAR,
        "measurement_method": "Flow cytometry",
        "key_features": ["senescence marker", "cell cycle arrest"],
        "expected_go_terms": ["GO:0090398"],
        "expected_genes": ["CDKN2A"],
        "validation_studies": ["PMID:26270257"],
        "year_published": 2015,
        "search_queries": [
            "p16INK4a senescence marker",
            "CDKN2A aging biomarker",
            "p16 cellular senescence"
        ]
    },
    {
        "name": "C-Reactive Protein",
        "category": bm.BiomarkerCategory.PROTEOMIC,
        "measurement_method": "Immunoassay",
        "key_features": ["inflammation marker", "cardiovascular risk"],
        "expected_uniprot": ["P02741"],
        "expected_kegg": ["hsa04610"],
        "validation_studies": ["PMID:24222477"],
        "year_published": 2013,
        "search_queries": [
            "CRP aging inflammation",
            "C-reactive protein aging biomarker",
            "high-sensitivity CRP aging"
        ]
    },
    {
        "name": "IL-6",
        "category": bm.BiomarkerCategory.PROTEOMIC,
        "measurement_method": "ELISA",
        "key_features": ["pro-inflammatory cytokine", "SASP factor"],
        "expected_uniprot": ["P05231"],
        "expected_go_terms": ["GO:0006954"],
        "expected_kegg": ["hsa04630"],
        "validation_studies": ["PMID:29727683"],
        "year_published": 2018,
        "search_queries": [
            "IL-6 aging inflammation",
            "interleukin-6 senescence",
            "IL-6 SASP biomarker"
        ]
    }
]


class ValidationDataset:
  """Golden dataset for validation testing."""
  
  def __init__(self):
    """Initialize validation dataset."""
    self.biomarkers = GOLDEN_BIOMARKERS
  
  def get_by_category(
      self,
      category: bm.BiomarkerCategory
  ) -> List[Dict]:
    """Get biomarkers by category."""
    return [
        b for b in self.biomarkers
        if b["category"] == category
    ]
  
  def get_search_queries(self) -> List[str]:
    """Get all search queries for validation."""
    queries = []
    for biomarker in self.biomarkers:
      queries.extend(biomarker["search_queries"])
    return queries
  
  def validate_extraction(
      self,
      extracted_biomarker: bm.BiomarkerEntity,
      expected_biomarker: Dict
  ) -> Dict:
    """Validate extracted biomarker against expected.
    
    Args:
      extracted_biomarker: BiomarkerEntity extracted from paper.
      expected_biomarker: Expected biomarker from golden dataset.
    
    Returns:
      Validation results with scores.
    """
    results = {
        "biomarker_name": expected_biomarker["name"],
        "category_match": False,
        "method_match": False,
        "ontology_match": False,
        "validation_score": 0
    }
    
    if extracted_biomarker.category == expected_biomarker["category"]:
      results["category_match"] = True
      results["validation_score"] += 25
    
    if expected_biomarker["measurement_method"].lower() in extracted_biomarker.measurement_method.lower():
      results["method_match"] = True
      results["validation_score"] += 25
    
    expected_go = set(expected_biomarker.get("expected_go_terms", []))
    extracted_go = set(extracted_biomarker.controlled_terms.go_terms)
    
    if expected_go & extracted_go:
      results["ontology_match"] = True
      results["validation_score"] += 25
    
    if extracted_biomarker.validation_status and extracted_biomarker.validation_status.is_validated:
      results["validation_score"] += 25
    
    return results
  
  def get_statistics(self) -> Dict:
    """Get dataset statistics."""
    categories = {}
    for biomarker in self.biomarkers:
      cat = biomarker["category"].value
      categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_biomarkers": len(self.biomarkers),
        "categories": categories,
        "total_queries": len(self.get_search_queries()),
        "year_range": (
            min(b["year_published"] for b in self.biomarkers),
            max(b["year_published"] for b in self.biomarkers)
        )
    }
  
  def export_to_json(self, filepath: str) -> None:
    """Export dataset to JSON file."""
    import json
    
    exportable = []
    for biomarker in self.biomarkers:
      export_item = biomarker.copy()
      export_item["category"] = biomarker["category"].value
      exportable.append(export_item)
    
    with open(filepath, 'w') as f:
      json.dump(exportable, f, indent=2)
    
    print(f"Exported {len(exportable)} biomarkers to {filepath}")


def print_dataset_summary():
  """Print summary of validation dataset."""
  dataset = ValidationDataset()
  stats = dataset.get_statistics()
  
  print("="*60)
  print("GOLDEN VALIDATION DATASET SUMMARY")
  print("="*60)
  print(f"Total biomarkers: {stats['total_biomarkers']}")
  print(f"Total search queries: {stats['total_queries']}")
  print(f"Year range: {stats['year_range'][0]}-{stats['year_range'][1]}")
  print(f"\nBy category:")
  for cat, count in sorted(stats['categories'].items()):
    print(f"  {cat}: {count}")
  
  print(f"\nBiomarkers:")
  for i, biomarker in enumerate(dataset.biomarkers, 1):
    print(f"  {i}. {biomarker['name']} ({biomarker['year_published']})")
    print(f"     Category: {biomarker['category'].value}")
    print(f"     Method: {biomarker['measurement_method']}")


if __name__ == "__main__":
  print_dataset_summary()
