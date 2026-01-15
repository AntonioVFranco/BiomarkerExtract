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

"""Accuracy metrics for biomarker extraction validation."""

from __future__ import annotations

from typing import Dict, List

from langextract.core import biomarker_models as bm


class AccuracyMetrics:
  """Calculate accuracy metrics for biomarker extraction."""
  
  def __init__(self):
    """Initialize metrics calculator."""
    self.predictions = []
    self.ground_truth = []
  
  def add_prediction(
      self,
      predicted: bm.BiomarkerEntity,
      expected: Dict
  ) -> None:
    """Add prediction for evaluation.
    
    Args:
      predicted: Extracted biomarker entity.
      expected: Expected biomarker from golden dataset.
    """
    self.predictions.append(predicted)
    self.ground_truth.append(expected)
  
  def calculate_category_accuracy(self) -> float:
    """Calculate category classification accuracy.
    
    Returns:
      Accuracy score 0-1.
    """
    if not self.predictions:
      return 0.0
    
    correct = sum(
        1 for pred, truth in zip(self.predictions, self.ground_truth)
        if pred.category == truth["category"]
    )
    
    return correct / len(self.predictions)
  
  def calculate_ontology_precision(self) -> float:
    """Calculate precision for ontology term extraction.
    
    Returns:
      Precision score 0-1.
    """
    if not self.predictions:
      return 0.0
    
    precisions = []
    
    for pred, truth in zip(self.predictions, self.ground_truth):
      expected_go = set(truth.get("expected_go_terms", []))
      predicted_go = set(pred.controlled_terms.go_terms)
      
      if not predicted_go:
        precisions.append(0.0)
        continue
      
      true_positives = len(expected_go & predicted_go)
      precision = true_positives / len(predicted_go)
      precisions.append(precision)
    
    return sum(precisions) / len(precisions)
  
  def calculate_ontology_recall(self) -> float:
    """Calculate recall for ontology term extraction.
    
    Returns:
      Recall score 0-1.
    """
    if not self.predictions:
      return 0.0
    
    recalls = []
    
    for pred, truth in zip(self.predictions, self.ground_truth):
      expected_go = set(truth.get("expected_go_terms", []))
      predicted_go = set(pred.controlled_terms.go_terms)
      
      if not expected_go:
        continue
      
      true_positives = len(expected_go & predicted_go)
      recall = true_positives / len(expected_go)
      recalls.append(recall)
    
    return sum(recalls) / len(recalls) if recalls else 0.0
  
  def calculate_f1_score(self) -> float:
    """Calculate F1 score for ontology extraction.
    
    Returns:
      F1 score 0-1.
    """
    precision = self.calculate_ontology_precision()
    recall = self.calculate_ontology_recall()
    
    if precision + recall == 0:
      return 0.0
    
    return 2 * (precision * recall) / (precision + recall)
  
  def calculate_validation_accuracy(self) -> float:
    """Calculate accuracy of validation status detection.
    
    Returns:
      Accuracy score 0-1.
    """
    if not self.predictions:
      return 0.0
    
    correct = sum(
        1 for pred, truth in zip(self.predictions, self.ground_truth)
        if (pred.validation_status and pred.validation_status.is_validated)
        == bool(truth.get("validation_studies"))
    )
    
    return correct / len(self.predictions)
  
  def calculate_confidence_correlation(self) -> float:
    """Calculate correlation between confidence and validation score.
    
    Returns:
      Correlation coefficient.
    """
    if len(self.predictions) < 2:
      return 0.0
    
    confidences = [pred.confidence for pred in self.predictions]
    val_scores = [
        pred.calculate_validation_score() for pred in self.predictions
    ]
    
    try:
      import numpy as np
      correlation = np.corrcoef(confidences, val_scores)[0, 1]
      return correlation if not np.isnan(correlation) else 0.0
    except ImportError:
      mean_conf = sum(confidences) / len(confidences)
      mean_val = sum(val_scores) / len(val_scores)
      
      numerator = sum(
          (c - mean_conf) * (v - mean_val)
          for c, v in zip(confidences, val_scores)
      )
      
      denom_conf = sum((c - mean_conf) ** 2 for c in confidences) ** 0.5
      denom_val = sum((v - mean_val) ** 2 for v in val_scores) ** 0.5
      
      if denom_conf * denom_val == 0:
        return 0.0
      
      return numerator / (denom_conf * denom_val)
  
  def get_all_metrics(self) -> Dict:
    """Calculate all accuracy metrics.
    
    Returns:
      Dictionary with all metrics.
    """
    return {
        "category_accuracy": self.calculate_category_accuracy(),
        "ontology_precision": self.calculate_ontology_precision(),
        "ontology_recall": self.calculate_ontology_recall(),
        "ontology_f1": self.calculate_f1_score(),
        "validation_accuracy": self.calculate_validation_accuracy(),
        "confidence_correlation": self.calculate_confidence_correlation(),
        "total_predictions": len(self.predictions)
    }
  
  def print_report(self) -> None:
    """Print comprehensive metrics report."""
    metrics = self.get_all_metrics()
    
    print("="*60)
    print("ACCURACY METRICS REPORT")
    print("="*60)
    print(f"\nTotal Predictions: {metrics['total_predictions']}")
    print(f"\nCategory Classification:")
    print(f"  Accuracy: {metrics['category_accuracy']:.2%}")
    print(f"\nOntology Term Extraction:")
    print(f"  Precision: {metrics['ontology_precision']:.2%}")
    print(f"  Recall: {metrics['ontology_recall']:.2%}")
    print(f"  F1 Score: {metrics['ontology_f1']:.2%}")
    print(f"\nValidation Detection:")
    print(f"  Accuracy: {metrics['validation_accuracy']:.2%}")
    print(f"\nConfidence-Quality Correlation:")
    print(f"  Correlation: {metrics['confidence_correlation']:.3f}")
    
    print(f"\n{'='*60}")
    print("INTERPRETATION")
    print("="*60)
    
    overall_score = (
        metrics['category_accuracy'] * 0.3 +
        metrics['ontology_f1'] * 0.4 +
        metrics['validation_accuracy'] * 0.3
    )
    
    print(f"Overall Score: {overall_score:.2%}")
    
    if overall_score >= 0.85:
      grade = "EXCELLENT"
    elif overall_score >= 0.70:
      grade = "GOOD"
    elif overall_score >= 0.50:
      grade = "FAIR"
    else:
      grade = "NEEDS IMPROVEMENT"
    
    print(f"Grade: {grade}")


class ConfusionMatrix:
  """Confusion matrix for biomarker category classification."""
  
  def __init__(self, categories: List[bm.BiomarkerCategory]):
    """Initialize confusion matrix.
    
    Args:
      categories: List of biomarker categories.
    """
    self.categories = categories
    self.matrix = {
        cat: {c: 0 for c in categories}
        for cat in categories
    }
  
  def add(
      self,
      predicted: bm.BiomarkerCategory,
      actual: bm.BiomarkerCategory
  ) -> None:
    """Add prediction to confusion matrix."""
    self.matrix[actual][predicted] += 1
  
  def print_matrix(self) -> None:
    """Print confusion matrix."""
    print("\n" + "="*60)
    print("CONFUSION MATRIX")
    print("="*60)
    print("\nRows = Actual, Columns = Predicted\n")
    
    cat_names = [c.value[:10] for c in self.categories]
    
    header = "Actual".ljust(12) + " ".join(c.ljust(10) for c in cat_names)
    print(header)
    print("-" * len(header))
    
    for actual in self.categories:
      row = actual.value[:10].ljust(12)
      for predicted in self.categories:
        count = self.matrix[actual][predicted]
        row += str(count).ljust(10)
      print(row)
  
  def calculate_per_category_metrics(self) -> Dict:
    """Calculate precision, recall, F1 per category.
    
    Returns:
      Dictionary with per-category metrics.
    """
    metrics = {}
    
    for category in self.categories:
      true_positives = self.matrix[category][category]
      
      false_positives = sum(
          self.matrix[other][category]
          for other in self.categories
          if other != category
      )
      
      false_negatives = sum(
          self.matrix[category][other]
          for other in self.categories
          if other != category
      )
      
      precision = (
          true_positives / (true_positives + false_positives)
          if true_positives + false_positives > 0
          else 0.0
      )
      
      recall = (
          true_positives / (true_positives + false_negatives)
          if true_positives + false_negatives > 0
          else 0.0
      )
      
      f1 = (
          2 * (precision * recall) / (precision + recall)
          if precision + recall > 0
          else 0.0
      )
      
      metrics[category.value] = {
          "precision": precision,
          "recall": recall,
          "f1": f1,
          "support": sum(self.matrix[category].values())
      }
    
    return metrics


def run_accuracy_evaluation(
    predictions: List[bm.BiomarkerEntity],
    ground_truth: List[Dict]
) -> Dict:
  """Run complete accuracy evaluation.
  
  Args:
    predictions: List of predicted biomarker entities.
    ground_truth: List of expected biomarkers from golden dataset.
  
  Returns:
    Complete evaluation results.
  """
  metrics = AccuracyMetrics()
  
  for pred, truth in zip(predictions, ground_truth):
    metrics.add_prediction(pred, truth)
  
  metrics.print_report()
  
  return metrics.get_all_metrics()


if __name__ == "__main__":
  print("Accuracy Metrics Module")
  print("Import this module to calculate extraction accuracy")
