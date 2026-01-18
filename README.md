<div align="center">

<img width="1280" height="720" alt="banner-bioexct-github" src="https://github.com/user-attachments/assets/a477b24b-01c9-478d-a3d5-aa805412031a" />



# BiomarkerExtract

**AI-Powered Biomarker Discovery from Scientific Literature**

[![Version](https://img.shields.io/badge/version-0.1-blue.svg)](https://github.com/AntonioVFranco/BiomarkerExtract/releases)
[![Python](https://img.shields.io/badge/python-3.12+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](https://github.com/AntonioVFranco/BiomarkerExtract)
[![Tests](https://img.shields.io/badge/tests-93%25%20passing-success.svg)](tests/)
[![Medium](https://img.shields.io/badge/Medium-Follow-black?logo=medium&logoColor=white)](https://medium.com/@AntonioVFranco)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/antoniovfranco/)

*Automated extraction and validation of aging biomarkers using state-of-the-art Large Language Models*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Results](#-results) • [Citation](#-citation)

</div>

---

## Contact

**Feel free to contact me via email for any needs:** contact@antoniovfranco.com

---

## Overview

BiomarkerExtract is a production-ready pipeline for discovering and validating aging biomarkers from scientific literature using Large Language Models. Built on Google's LangExtract framework, it supports multiple LLM providers and delivers publication-quality results at ultra-low cost.

###  Key Achievements

- ✅ **79 biomarkers extracted** from 46 scientific papers
- ✅ **93.7% validation rate** with scientific evidence
- ✅ **84.8% high confidence** (≥0.90) extractions
- ✅ **$0.003 per paper** processing cost
- ✅ **5 LLM providers** supported out-of-the-box

---

## Features

### Multi-Provider LLM Support
- **OpenRouter** - 100+ models with single API key (Recommended)
- **OpenAI** - GPT-5.2, GPT-4o, O1
- **Anthropic** - Claude 4.5, Sonnet 4.5
- **Google** - Gemini 3.0, Gemini Pro
- **Ollama** - Local inference (FREE)

### Complete Pipeline
1. **Literature Search** - PubMed + bioRxiv integration
2. **Biomarker Extraction** - LLM-powered entity recognition
3. **Scientific Validation** - Automated quality assessment
4. **Multi-Format Export** - JSON, CSV, TXT

### Analysis & Visualization
- Publication-quality charts
- Network analysis
- Category distribution
- Confidence metrics
- Sample size statistics

---

## Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/AntonioVFranco/BiomarkerExtract.git
cd BiomarkerExtract

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run installation
bash install_unified.sh
```

### Configuration
```bash
# Set your API key (choose one provider)
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxx"  # Recommended
# OR
export OPENAI_API_KEY="sk-xxxxxxxx"
# OR
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxx"
```

### Run Pipeline
```bash
# Quick start with OpenRouter (cheapest)
bash run_openrouter.sh

# Or with other providers
bash run_openai.sh      # OpenAI GPT-5.2
bash run_anthropic.sh   # Claude 4.5
bash run_ollama.sh      # Local (FREE)
```

### Python API
```python
from langextract.providers import unified_production_pipeline as upp

results = upp.run_pipeline(
    biomarker_terms=["Horvath clock", "GDF-15", "NAD+"],
    pubmed_email="your.email@domain.com",
    provider="openrouter",
    api_key="your-key",
    max_papers=20
)

print(f"Extracted {results['statistics']['biomarkers_extracted']} biomarkers!")
```

---

## Results

### Sample Extraction (v0.1)

| Metric | Value |
|--------|-------|
| Papers Processed | 46 |
| Biomarkers Extracted | 79 |
| Validated | 74 (93.7%) |
| High Confidence | 67 (84.8%) |
| Processing Time | 8.35 minutes |
| Total Cost | $0.15 |

### Top Biomarkers Discovered

1. **Horvath clock** (12 mentions) - Epigenetic
2. **GDF-15** (9 mentions) - Proteomic
3. **NAD+ levels** (3 mentions) - Metabolomic
4. **Hannum clock** (2 mentions) - Epigenetic
5. **DunedinPACE** (2 mentions) - Epigenetic

### Category Distribution

- Epigenetic: 43.0%
- Proteomic: 34.2%
- Cellular: 10.1%
- Metabolomic: 6.3%
- Genomic: 2.5%
- Transcriptomic: 2.5%

---

## Documentation

- **[UNIFIED_README.md](UNIFIED_README.md)** - Complete system overview
- **[UNIFIED_CONFIGURATION.md](UNIFIED_CONFIGURATION.md)** - Provider setup guides
- **[Phase3_README.md](Phase3_README.md)** - Core biomarker models
- **[Phase4_README.md](Phase4_README.md)** - Literature pipeline
- **[Option2_Testing_README.md](Option2_Testing_README.md)** - Testing suite

### Examples

See [examples_unified.py](examples_unified.py) for 9 complete working examples:
- Basic extraction
- Batch processing
- Provider comparison
- Custom models
- Complete pipeline

---

## Cost Comparison

Processing 1000 papers:

| Provider | Cost | Speed | Accuracy |
|----------|------|-------|----------|
| **OpenRouter** | **$3.00** ⭐ | Fast | 88% |
| OpenAI GPT-5.2 | $25.00 | Fast | 92% |
| Anthropic Claude 4.5 | $30.00 | Medium | 90% |
| Google Gemini 3.0 | $10.00 | Fast | 85% |
| Ollama | **FREE** ⭐ | Slow* | 80% |

*Depends on local GPU

---

## Architecture
```
BiomarkerExtract/
├── langextract/
│   ├── core/
│   │   └── biomarker_models.py      # 21 Pydantic models
│   ├── literature/
│   │   ├── pubmed_client.py         # PubMed API
│   │   ├── biorxiv_client.py        # bioRxiv API
│   │   ├── pdf_parser.py            # PDF extraction
│   │   └── batch_processor.py       # Parallel processing
│   └── providers/
│       ├── unified_llm_provider.py           # 5 LLM providers
│       └── unified_production_pipeline.py    # End-to-end pipeline
├── tests/
│   └── option2/                     # 30+ tests (93% passing)
├── examples_unified.py              # 9 working examples
└── run_*.sh                         # Quick-start scripts
```

---

## Testing
```bash
# Run complete test suite
cd tests/option2
bash full_test.sh

# Quick validation
bash quick_test.sh

# Results: 93% tests passing
```

---

## Statistics

- **~5,700 lines** of production code
- **21 Pydantic models** for data validation
- **5 LLM providers** integrated
- **30+ unit tests** (93% success rate)
- **3 formats** for data export (JSON, CSV, TXT)
- **Publication-quality** visualizations included

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

Based on [Google's LangExtract](https://github.com/google/langextract) framework.

---

## Citation

If you use BiomarkerExtract in your research, please cite:
```bibtex
@software{biomarkerextract2026,
  author = {Franco, Antonio V.},
  title = {BiomarkerExtract: AI-Powered Biomarker Discovery from Scientific Literature},
  year = {2026},
  version = {0.1},
  url = {https://github.com/AntonioVFranco/BiomarkerExtract}
}
```

---

## Acknowledgments

- Built on [Google's LangExtract](https://github.com/google/langextract)
- Inspired by aging research and longevity science
- Powered by state-of-the-art Large Language Models

---

## Connect

- Email: contact@antoniovfranco.com
- Medium: [@AntonioVFranco](https://medium.com/@AntonioVFranco)
- LinkedIn: [antoniovfranco](https://www.linkedin.com/in/antoniovfranco/)
- GitHub: [@AntonioVFranco](https://github.com/AntonioVFranco)

---

<div align="center">

⭐ **Star this repo if you find it useful!** ⭐

[Report Bug](https://github.com/AntonioVFranco/BiomarkerExtract/issues) • [Request Feature](https://github.com/AntonioVFranco/BiomarkerExtract/issues) • [Documentation](docs/)

</div>
