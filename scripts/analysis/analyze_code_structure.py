"""
BiomarkerExtract Phase 2: Code Structure Analysis
Analyzes LangExtract architecture to identify biomarker extension points
"""

import os
import ast
from pathlib import Path
from typing import List, Dict, Set

def analyze_python_file(filepath: Path) -> Dict:
    """Analyze Python file to extract classes, functions, and imports."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                classes.append({
                    'name': node.name,
                    'methods': methods,
                    'bases': [base.id for base in node.bases if isinstance(base, ast.Name)]
                })
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                functions.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(node.module)
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': list(set(imports))
        }
    except Exception as e:
        return {'error': str(e)}

def scan_directory(base_path: Path, target_dir: str) -> Dict:
    """Scan directory for Python files and analyze structure."""
    target_path = base_path / target_dir
    if not target_path.exists():
        return {}
    
    results = {}
    for py_file in target_path.rglob('*.py'):
        if '__pycache__' not in str(py_file) and 'venv' not in str(py_file):
            rel_path = py_file.relative_to(base_path)
            results[str(rel_path)] = analyze_python_file(py_file)
    
    return results

def main():
    base_path = Path.cwd()
    
    print("=" * 70)
    print("BIOMARKEREXTRACT ARCHITECTURE ANALYSIS - CODE STRUCTURE")
    print("=" * 70)
    print()
    
    # Analyze core modules
    print("1. CORE EXTRACTION ENGINE")
    print("-" * 70)
    core_analysis = scan_directory(base_path, 'langextract/core')
    for file_path, analysis in sorted(core_analysis.items()):
        if 'error' not in analysis:
            print(f"\n{file_path}:")
            if analysis['classes']:
                print(f"  Classes: {[c['name'] for c in analysis['classes']]}")
                for cls in analysis['classes']:
                    if cls['methods']:
                        print(f"    {cls['name']} methods: {cls['methods'][:5]}")
            if analysis['functions']:
                print(f"  Functions: {analysis['functions'][:5]}")
    
    # Analyze providers
    print("\n\n2. PROVIDER IMPLEMENTATIONS")
    print("-" * 70)
    provider_analysis = scan_directory(base_path, 'langextract/providers')
    for file_path, analysis in sorted(provider_analysis.items()):
        if 'error' not in analysis and analysis['classes']:
            print(f"\n{file_path}:")
            for cls in analysis['classes']:
                print(f"  Class: {cls['name']}")
                if cls['bases']:
                    print(f"    Inherits from: {cls['bases']}")
                if cls['methods']:
                    print(f"    Key methods: {cls['methods'][:8]}")
    
    # Identify extension points
    print("\n\n3. EXTENSION POINTS FOR BIOMARKER CUSTOMIZATION")
    print("-" * 70)
    print("""
Based on code analysis, identified extension points:

A. Custom Schema Creation (langextract/core/schema.py)
   - Define BiomarkerEntity with aging-specific fields
   - Add Statistics validation with p-value thresholds
   - Implement ControlledTerms for GO/KEGG/UniProt mapping

B. Custom Provider (langextract/providers/gemini_biomarker.py)
   - Extend base provider with biomarker-specific prompts
   - Add few-shot examples for aging research
   - Implement domain-specific post-processing

C. Validation Layer (langextract/core/validator.py)
   - Add biomarker-specific validation rules
   - Implement ontology verification
   - Check statistical significance requirements

D. Chunking Strategy (langextract/chunking/)
   - Customize for scientific paper sections
   - Prioritize Results and Methods sections
   - Handle tables and figures references
    """)
    
    # Summary
    print("\n\n4. MODIFICATION STRATEGY SUMMARY")
    print("-" * 70)
    print("""
RECOMMENDED APPROACH:

Phase 2a: Non-Breaking Extensions
- Create langextract/core/biomarker_schema.py
- Add langextract/providers/gemini_biomarker.py
- Keep original LangExtract functionality intact

Phase 2b: Biomarker-Specific Features
- Add relationship extraction module
- Implement contradiction detection
- Create visualization for biomarker networks

Phase 2c: Literature Integration
- Add PubMed/bioRxiv connectors
- Implement PDF parsing for papers
- Create batch processing pipeline

SUCCESS CRITERIA:
- F1 score > 0.85 on biomarker extraction
- All ontology terms validated
- Zero breaking changes to core LangExtract
    """)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE - Ready for Phase 3: Implementation")
    print("=" * 70)

if __name__ == '__main__':
    main()
