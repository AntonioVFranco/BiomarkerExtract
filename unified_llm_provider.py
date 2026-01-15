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

"""Unified LLM provider: OpenRouter, OpenAI GPT-5.2, Claude 4.5, Gemini 3.0."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

import requests


try:
  from langextract.core import biomarker_models as bm
except ImportError:
  import sys
  sys.path.append('..')
  from langextract.core import biomarker_models as bm


class UnifiedLLMProvider:
  """Unified provider with latest models: GPT-5.2, Claude 4.5, Gemini 3.0."""
  
  OPENROUTER_MODELS = {
      "deepseek-r1": "deepseek/deepseek-r1",
      "deepseek-chat": "deepseek/deepseek-chat",
      "qwen-2.5-72b": "qwen/qwen-2.5-72b-instruct",
      "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct",
      "gpt-5.2": "openai/gpt-5.2",
      "claude-4.5": "anthropic/claude-4.5",
      "gemini-3.0": "google/gemini-3.0",
      "mistral-large": "mistralai/mistral-large-2411"
  }
  
  OPENAI_MODELS = {
      "gpt-5.2": "gpt-5.2",
      "gpt-5": "gpt-5",
      "gpt-4o": "gpt-4o",
      "o1": "o1"
  }
  
  ANTHROPIC_MODELS = {
      "claude-4.5": "claude-4.5",
      "claude-sonnet-4.5": "claude-sonnet-4.5-20250110",
      "claude-opus-4.5": "claude-opus-4.5"
  }
  
  GEMINI_MODELS = {
      "gemini-3.0": "gemini-3.0",
      "gemini-3.0-pro": "gemini-3.0-pro",
      "gemini-3.0-flash": "gemini-3.0-flash"
  }
  
  DEFAULT_MODELS = {
      "openrouter": "deepseek-chat",
      "openai": "gpt-5.2",
      "anthropic": "claude-4.5",
      "gemini": "gemini-3.0",
      "ollama": "llama3.3"
  }
  
  def __init__(
      self,
      provider: str = "openrouter",
      model: Optional[str] = None,
      api_key: Optional[str] = None,
      temperature: float = 0.1,
      max_tokens: int = 4000
  ):
    """Initialize unified LLM provider.
    
    Args:
      provider: Provider (openrouter, openai, anthropic, gemini, ollama).
      model: Model name. If None, uses DEFAULT_MODELS for provider.
            Can be any custom model string for flexibility.
      api_key: API key for the service.
      temperature: Sampling temperature.
      max_tokens: Maximum tokens to generate.
    """
    self.provider = provider.lower()
    
    if model is None:
      model = self.DEFAULT_MODELS.get(self.provider, "gpt-5.2")
    
    self.model = model
    self.temperature = temperature
    self.max_tokens = max_tokens
    
    if self.provider == "openrouter":
      self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
      self.api_base = "https://openrouter.ai/api/v1"
      self.model_id = self.OPENROUTER_MODELS.get(model, model)
    
    elif self.provider == "openai":
      self.api_key = api_key or os.getenv("OPENAI_API_KEY")
      self.api_base = "https://api.openai.com/v1"
      self.model_id = self.OPENAI_MODELS.get(model, model)
    
    elif self.provider == "anthropic":
      self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
      self.api_base = "https://api.anthropic.com/v1"
      self.model_id = self.ANTHROPIC_MODELS.get(model, model)
    
    elif self.provider == "gemini":
      self.api_key = api_key or os.getenv("GEMINI_API_KEY")
      self.api_base = "https://generativelanguage.googleapis.com/v1beta"
      self.model_id = self.GEMINI_MODELS.get(model, model)
    
    elif self.provider == "ollama":
      self.api_key = "ollama"
      self.api_base = "http://localhost:11434/v1"
      self.model_id = model
    
    else:
      raise ValueError(f"Unsupported provider: {provider}")
    
    if not self.api_key and self.provider != "ollama":
      raise ValueError(f"API key required for {provider}")
    
    self.session = requests.Session()
    if self.api_key and self.provider != "gemini":
      self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
  
  def create_biomarker_prompt(self, text: str) -> str:
    """Create prompt for biomarker extraction."""
    return f"""You are an expert in aging research and biomarker extraction. Extract all aging biomarkers mentioned in the following scientific text.

For each biomarker, provide:
1. name: The biomarker name
2. category: One of [epigenetic, proteomic, metabolomic, genomic, transcriptomic, cellular, multi_omics]
3. measurement_method: How it is measured
4. finding: Key finding about this biomarker
5. statistics: Include p_value and sample_size if mentioned
6. validation_status: Whether it has been validated
7. controlled_terms: Gene symbols, GO terms, KEGG pathways if applicable
8. confidence: Your confidence score (0.0-1.0)

Text:
{text}

Respond ONLY with valid JSON in this exact format:
{{
  "biomarkers": [
    {{
      "name": "Horvath clock",
      "category": "epigenetic",
      "measurement_method": "DNA methylation array",
      "finding": "Predicts chronological age with high accuracy",
      "statistics": {{"p_value": 0.001, "sample_size": 1200}},
      "validation_status": {{"is_validated": true}},
      "controlled_terms": {{"go_terms": ["GO:0006306"], "gene_symbols": ["DNMT1"]}},
      "confidence": 0.95
    }}
  ]
}}"""
  
  def extract_biomarkers(
      self,
      text: str,
      return_raw: bool = False
  ) -> bm.BiomarkerExtraction:
    """Extract biomarkers from text using LLM."""
    
    if self.provider == "anthropic":
      return self._extract_anthropic(text, return_raw)
    elif self.provider == "gemini":
      return self._extract_gemini(text, return_raw)
    else:
      return self._extract_openai_compatible(text, return_raw)
  
  def _extract_openai_compatible(
      self,
      text: str,
      return_raw: bool
  ) -> bm.BiomarkerExtraction:
    """Extract using OpenAI-compatible API (OpenRouter, OpenAI, Ollama)."""
    
    prompt = self.create_biomarker_prompt(text)
    
    payload = {
        "model": self.model_id,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert biomarker extraction system. Respond only with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": self.temperature,
        "max_tokens": self.max_tokens
    }
    
    if self.provider == "openrouter":
      payload["response_format"] = {"type": "json_object"}
      self.session.headers.update({
          "HTTP-Referer": "https://github.com/biomarkerextract",
          "X-Title": "BiomarkerExtract"
      })
    
    response = self.session.post(
        f"{self.api_base}/chat/completions",
        json=payload,
        timeout=60
    )
    
    response.raise_for_status()
    result = response.json()
    
    content = result["choices"][0]["message"]["content"]
    
    if return_raw:
      return content
    
    return self._parse_response(content, text)
  
  def _extract_anthropic(
      self,
      text: str,
      return_raw: bool
  ) -> bm.BiomarkerExtraction:
    """Extract using Anthropic Claude 4.5 API."""
    
    prompt = self.create_biomarker_prompt(text)
    
    payload = {
        "model": self.model_id,
        "max_tokens": self.max_tokens,
        "temperature": self.temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    headers = {
        "x-api-key": self.api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    response = requests.post(
        f"{self.api_base}/messages",
        json=payload,
        headers=headers,
        timeout=60
    )
    
    response.raise_for_status()
    result = response.json()
    
    content = result["content"][0]["text"]
    
    if return_raw:
      return content
    
    return self._parse_response(content, text)
  
  def _extract_gemini(
      self,
      text: str,
      return_raw: bool
  ) -> bm.BiomarkerExtraction:
    """Extract using Gemini 3.0 API."""
    
    prompt = self.create_biomarker_prompt(text)
    
    url = f"{self.api_base}/models/{self.model_id}:generateContent?key={self.api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": self.temperature,
            "maxOutputTokens": self.max_tokens
        }
    }
    
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    
    content = result["candidates"][0]["content"]["parts"][0]["text"]
    
    if return_raw:
      return content
    
    return self._parse_response(content, text)
  
  def _parse_response(
      self,
      content: str,
      original_text: str
  ) -> bm.BiomarkerExtraction:
    """Parse LLM response into BiomarkerExtraction."""
    
    try:
      data = json.loads(content)
    except json.JSONDecodeError:
      content_clean = content.strip()
      if content_clean.startswith("```json"):
        content_clean = content_clean[7:]
      if content_clean.endswith("```"):
        content_clean = content_clean[:-3]
      
      data = json.loads(content_clean.strip())
    
    entities = []
    
    for biomarker_data in data.get("biomarkers", []):
      try:
        category_str = biomarker_data.get("category", "multi_omics")
        category = bm.BiomarkerCategory(category_str)
        
        statistics = None
        stats_data = biomarker_data.get("statistics")
        if stats_data:
          statistics = bm.Statistics(
              p_value=stats_data.get("p_value"),
              sample_size=stats_data.get("sample_size")
          )
        
        validation_status = None
        val_data = biomarker_data.get("validation_status")
        if val_data:
          validation_status = bm.ValidationStatus(
              is_validated=val_data.get("is_validated", False)
          )
        
        controlled_terms = None
        terms_data = biomarker_data.get("controlled_terms")
        if terms_data:
          controlled_terms = bm.ControlledTerms(
              go_terms=terms_data.get("go_terms", []),
              kegg_pathways=terms_data.get("kegg_pathways", []),
              gene_symbols=terms_data.get("gene_symbols", [])
          )
        
        entity = bm.BiomarkerEntity(
            name=biomarker_data["name"],
            category=category,
            measurement_method=biomarker_data.get("measurement_method", "Not specified"),
            finding=biomarker_data.get("finding", ""),
            statistics=statistics,
            validation_status=validation_status,
            controlled_terms=controlled_terms,
            confidence=biomarker_data.get("confidence", 0.8)
        )
        
        entities.append(entity)
      
      except Exception as e:
        print(f"Error parsing biomarker: {e}")
        continue
    
    return bm.BiomarkerExtraction(
        entities=entities,
        document_metadata={
            "provider": self.provider,
            "model": self.model_id,
            "text_length": len(original_text)
        },
        extraction_timestamp=bm.datetime.now().isoformat(),
        model_version=f"{self.provider}/{self.model_id}"
    )
  
  def batch_extract(
      self,
      texts: List[str],
      show_progress: bool = True
  ) -> List[bm.BiomarkerExtraction]:
    """Extract biomarkers from multiple texts."""
    results = []
    
    iterator = enumerate(texts, 1)
    if show_progress:
      try:
        from tqdm import tqdm
        iterator = tqdm(enumerate(texts, 1), total=len(texts), desc="Extracting")
      except ImportError:
        pass
    
    for i, text in iterator:
      try:
        extraction = self.extract_biomarkers(text)
        results.append(extraction)
      except Exception as e:
        print(f"Error processing text {i}: {e}")
        results.append(bm.BiomarkerExtraction(
            entities=[],
            document_metadata={"error": str(e)},
            extraction_timestamp=bm.datetime.now().isoformat(),
            model_version=f"{self.provider}/{self.model_id}"
        ))
    
    return results


def create_provider(
    provider: str = "openrouter",
    model: Optional[str] = None,
    **kwargs
) -> UnifiedLLMProvider:
  """Factory function to create LLM provider.
  
  Args:
    provider: Provider type (openrouter, openai, anthropic, gemini, ollama).
    model: Model name. If None, uses latest default for provider.
    **kwargs: Additional arguments.
  
  Returns:
    Configured UnifiedLLMProvider.
  
  Examples:
    # Use defaults (latest models)
    provider = create_provider("openai")  # Uses GPT-5.2
    provider = create_provider("anthropic")  # Uses Claude 4.5
    provider = create_provider("gemini")  # Uses Gemini 3.0
    
    # Custom models
    provider = create_provider("openai", model="gpt-4o")
    provider = create_provider("openrouter", model="deepseek-r1")
  """
  return UnifiedLLMProvider(provider=provider, model=model, **kwargs)


if __name__ == "__main__":
  print("Unified LLM Provider for BiomarkerExtract")
  print()
  print("Latest Models:")
  print(f"  OpenAI: GPT-5.2")
  print(f"  Anthropic: Claude 4.5")
  print(f"  Gemini: 3.0")
  print(f"  OpenRouter: 100+ models")
  print()
  print(f"Supported providers: openrouter, openai, anthropic, gemini, ollama")
