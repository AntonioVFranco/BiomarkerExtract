#!/usr/bin/env python3
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

"""Complete examples for all LLM providers."""

import os


def example_1_openrouter():
  """Example 1: OpenRouter with DeepSeek."""
  print("="*70)
  print("EXAMPLE 1: OpenRouter with DeepSeek")
  print("="*70)
  print()
  
  from langextract.providers import unified_llm_provider as ullm
  
  provider = ullm.UnifiedLLMProvider(
      provider="openrouter",
      model="deepseek-chat",
      api_key=os.getenv("OPENROUTER_API_KEY")
  )
  
  abstract = """
  DNA methylation age was developed by Horvath in 2013. It uses 353 CpG 
  sites to predict chronological age with high accuracy (r=0.96, p<0.001, 
  n=8000).
  """
  
  print("Extracting biomarkers...")
  extraction = provider.extract_biomarkers(abstract)
  
  print(f"Found {len(extraction.entities)} biomarkers:")
  for biomarker in extraction.entities:
    print(f"  - {biomarker.name} ({biomarker.category.value})")
  print()


def example_2_openai_gpt52():
  """Example 2: OpenAI GPT-5.2."""
  print("="*70)
  print("EXAMPLE 2: OpenAI GPT-5.2 (Latest)")
  print("="*70)
  print()
  
  from langextract.providers import unified_llm_provider as ullm
  
  provider = ullm.UnifiedLLMProvider(
      provider="openai",
      api_key=os.getenv("OPENAI_API_KEY")
  )
  
  print(f"Using model: {provider.model_id}")
  
  abstract = """
  Telomere length decreases with age (p<0.001, n=5000) and predicts 
  mortality risk. Measured by qPCR.
  """
  
  extraction = provider.extract_biomarkers(abstract)
  print(f"Extracted {len(extraction.entities)} biomarkers")
  print()


def example_3_anthropic_claude45():
  """Example 3: Anthropic Claude 4.5."""
  print("="*70)
  print("EXAMPLE 3: Anthropic Claude 4.5 (Latest)")
  print("="*70)
  print()
  
  from langextract.providers import unified_llm_provider as ullm
  
  provider = ullm.UnifiedLLMProvider(
      provider="anthropic",
      api_key=os.getenv("ANTHROPIC_API_KEY")
  )
  
  print(f"Using model: {provider.model_id}")
  
  abstract = """
  GDF-15 levels increase with age and predict mortality (HR=1.5, p<0.001, 
  n=10000). Associated with mitochondrial dysfunction.
  """
  
  extraction = provider.extract_biomarkers(abstract)
  print(f"Extracted {len(extraction.entities)} biomarkers")
  print()


def example_4_gemini_30():
  """Example 4: Gemini 3.0."""
  print("="*70)
  print("EXAMPLE 4: Gemini 3.0 (Latest)")
  print("="*70)
  print()
  
  from langextract.providers import unified_llm_provider as ullm
  
  provider = ullm.UnifiedLLMProvider(
      provider="gemini",
      api_key=os.getenv("GEMINI_API_KEY")
  )
  
  print(f"Using model: {provider.model_id}")
  
  abstract = """
  p16INK4a is a cellular senescence marker that increases with age. 
  Measured by flow cytometry.
  """
  
  extraction = provider.extract_biomarkers(abstract)
  print(f"Extracted {len(extraction.entities)} biomarkers")
  print()


def example_5_complete_pipeline():
  """Example 5: Complete pipeline with literature search."""
  print("="*70)
  print("EXAMPLE 5: Complete Pipeline (OpenRouter)")
  print("="*70)
  print()
  
  from langextract.providers import unified_production_pipeline as upp
  
  results = upp.run_pipeline(
      biomarker_terms=["Horvath clock", "GDF-15"],
      pubmed_email="biomarkerextract@test.com",
      provider="openrouter",
      model="deepseek-chat",
      api_key=os.getenv("OPENROUTER_API_KEY"),
      max_papers=5
  )
  
  print(f"Results: {results['statistics']['biomarkers_extracted']} biomarkers")
  print()


def example_6_compare_providers():
  """Example 6: Compare different providers."""
  print("="*70)
  print("EXAMPLE 6: Provider Comparison")
  print("="*70)
  print()
  
  from langextract.providers import unified_llm_provider as ullm
  import time
  
  abstract = """
  The Horvath clock uses DNA methylation to predict age with high accuracy.
  """
  
  providers_config = []
  
  if os.getenv("OPENROUTER_API_KEY"):
    providers_config.append(("OpenRouter", "openrouter", "deepseek-chat"))
  
  if os.getenv("OPENAI_API_KEY"):
    providers_config.append(("OpenAI GPT-5.2", "openai", None))
  
  if os.getenv("ANTHROPIC_API_KEY"):
    providers_config.append(("Claude 4.5", "anthropic", None))
  
  if os.getenv("GEMINI_API_KEY"):
    providers_config.append(("Gemini 3.0", "gemini", None))
  
  for name, provider_type, model in providers_config:
    print(f"Testing {name}...")
    start = time.time()
    
    try:
      provider = ullm.UnifiedLLMProvider(
          provider=provider_type,
          model=model
      )
      
      extraction = provider.extract_biomarkers(abstract)
      elapsed = time.time() - start
      
      print(f"  Model: {provider.model_id}")
      print(f"  Biomarkers: {len(extraction.entities)}")
      print(f"  Time: {elapsed:.2f}s")
    except Exception as e:
      print(f"  Error: {e}")
    
    print()


def example_7_custom_models():
  """Example 7: Using custom models."""
  print("="*70)
  print("EXAMPLE 7: Custom Model Configuration")
  print("="*70)
  print()
  
  from langextract.providers import unified_llm_provider as ullm
  
  configs = [
      ("OpenAI GPT-4o", "openai", "gpt-4o"),
      ("OpenRouter Llama", "openrouter", "llama-3.3-70b"),
      ("Claude Opus 4.5", "anthropic", "claude-opus-4.5")
  ]
  
  for name, provider_type, model in configs:
    try:
      provider = ullm.UnifiedLLMProvider(
          provider=provider_type,
          model=model
      )
      print(f"{name}: {provider.model_id} ✓")
    except Exception as e:
      print(f"{name}: {e}")
  
  print()


def example_8_batch_extraction():
  """Example 8: Batch extraction."""
  print("="*70)
  print("EXAMPLE 8: Batch Extraction")
  print("="*70)
  print()
  
  from langextract.providers import unified_llm_provider as ullm
  
  provider = ullm.UnifiedLLMProvider(
      provider="openrouter",
      model="deepseek-chat",
      api_key=os.getenv("OPENROUTER_API_KEY")
  )
  
  abstracts = [
      "Telomere length decreases with age.",
      "p16INK4a is a senescence marker.",
      "NAD+ levels decline with aging."
  ]
  
  print(f"Processing {len(abstracts)} abstracts...")
  extractions = provider.batch_extract(abstracts, show_progress=True)
  
  total = sum(len(e.entities) for e in extractions)
  print(f"Total biomarkers: {total}")
  print()


def example_9_ollama_local():
  """Example 9: Local Ollama."""
  print("="*70)
  print("EXAMPLE 9: Ollama Local (FREE)")
  print("="*70)
  print()
  
  try:
    from langextract.providers import unified_llm_provider as ullm
    
    provider = ullm.UnifiedLLMProvider(
        provider="ollama",
        model="llama3.3"
    )
    
    abstract = """
    IL-6 is a pro-inflammatory cytokine associated with cellular senescence.
    """
    
    extraction = provider.extract_biomarkers(abstract)
    print(f"Found {len(extraction.entities)} biomarkers")
    print("Ollama is working!")
    
  except Exception as e:
    print(f"Ollama not available: {e}")
    print("To use Ollama:")
    print("  1. Install: curl https://ollama.ai/install.sh | sh")
    print("  2. Pull model: ollama pull llama3.3")
    print("  3. Start server: ollama serve")
  
  print()


def main():
  """Run all examples."""
  print("\n" + "="*70)
  print("BIOMARKEREXTRACT - UNIFIED LLM PROVIDER EXAMPLES")
  print("="*70)
  print()
  
  print("Available examples:")
  print("  1. OpenRouter with DeepSeek")
  print("  2. OpenAI GPT-5.2")
  print("  3. Anthropic Claude 4.5")
  print("  4. Gemini 3.0")
  print("  5. Complete pipeline")
  print("  6. Compare providers")
  print("  7. Custom models")
  print("  8. Batch extraction")
  print("  9. Ollama local")
  print()
  
  choice = input("Choose example (1-9) or 'all': ").strip()
  
  if choice == "1":
    example_1_openrouter()
  elif choice == "2":
    example_2_openai_gpt52()
  elif choice == "3":
    example_3_anthropic_claude45()
  elif choice == "4":
    example_4_gemini_30()
  elif choice == "5":
    example_5_complete_pipeline()
  elif choice == "6":
    example_6_compare_providers()
  elif choice == "7":
    example_7_custom_models()
  elif choice == "8":
    example_8_batch_extraction()
  elif choice == "9":
    example_9_ollama_local()
  elif choice == "all":
    example_1_openrouter()
    example_6_compare_providers()
    example_7_custom_models()
    example_8_batch_extraction()
    example_9_ollama_local()
  else:
    print("Invalid choice")


if __name__ == "__main__":
  main()
