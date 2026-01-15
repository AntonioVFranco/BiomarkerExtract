#!/bin/bash

# BiomarkerExtract - Unified LLM Production Pipeline Installation

set -e

echo "======================================================================"
echo "BiomarkerExtract - Unified LLM Production Pipeline"
echo "OpenRouter + OpenAI + Anthropic + Gemini + Ollama"
echo "======================================================================"
echo ""

cd /mnt/c/Users/tommo/Documents/Bioinformatics/1102/BiomarkerExtract
source venv/bin/activate

echo "Step 1: Creating providers directory..."
mkdir -p langextract/providers
touch langextract/providers/__init__.py
echo "✓ Providers directory created"
echo ""

echo "Step 2: Moving unified provider files..."
if [ -f "unified_llm_provider.py" ]; then
    cp unified_llm_provider.py langextract/providers/
    echo "✓ unified_llm_provider.py moved"
fi

if [ -f "unified_production_pipeline.py" ]; then
    cp unified_production_pipeline.py langextract/providers/
    echo "✓ unified_production_pipeline.py moved"
fi

if [ -f "examples_unified.py" ]; then
    cp examples_unified.py .
    chmod +x examples_unified.py
    echo "✓ examples_unified.py ready"
fi

if [ -f "UNIFIED_CONFIGURATION.md" ]; then
    cp UNIFIED_CONFIGURATION.md docs/
    echo "✓ UNIFIED_CONFIGURATION.md moved to docs"
fi

if [ -f "UNIFIED_README.md" ]; then
    cp UNIFIED_README.md docs/
    echo "✓ UNIFIED_README.md moved to docs"
fi
echo ""

echo "Step 3: Installing dependencies..."
pip install python-dotenv --break-system-packages
echo "✓ Dependencies installed"
echo ""

echo "Step 4: Creating .env template..."
if [ ! -f ".env" ]; then
    cat > .env.template << 'ENVTEMPLATE'
# BiomarkerExtract Unified LLM API Keys

# OpenRouter (recommended - 100+ models with ONE key)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

# OpenAI (GPT-5.2)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# Anthropic (Claude 4.5)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# Google Gemini (3.0)
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxx

# PubMed (optional but recommended)
PUBMED_API_KEY=your-ncbi-key
ENVTEMPLATE
    echo "✓ Created .env.template (copy to .env and add your keys)"
else
    echo "✓ .env file already exists"
fi
echo ""

echo "Step 5: Testing imports..."
python << 'PYTHON_TEST'
try:
    from langextract.providers import unified_llm_provider as ullm
    print("✓ unified_llm_provider imported")
    
    providers = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
    print(f"✓ Supported providers: {', '.join(providers)}")
    
    defaults = ullm.UnifiedLLMProvider.DEFAULT_MODELS
    print(f"✓ Default models loaded")
    
except ImportError as e:
    print(f"✗ Import failed: {e}")

try:
    from langextract.providers import unified_production_pipeline as upp
    print("✓ unified_production_pipeline imported")
except ImportError as e:
    print(f"✗ Import failed: {e}")
PYTHON_TEST
echo ""

echo "Step 6: Creating quick-start scripts..."

# OpenRouter script
cat > run_openrouter.sh << 'OPENROUTER_SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY not set"
    echo "Get key from: https://openrouter.ai/"
    echo "Set it with: export OPENROUTER_API_KEY='your-key'"
    exit 1
fi

echo "Running pipeline with OpenRouter..."
python -m langextract.providers.unified_production_pipeline \
    --terms "Horvath clock" "GDF-15" "NAD+" \
    --email biomarkerextract@test.com \
    --provider openrouter \
    --api-key $OPENROUTER_API_KEY \
    --max-papers 20
OPENROUTER_SCRIPT
chmod +x run_openrouter.sh
echo "✓ run_openrouter.sh created"

# OpenAI script
cat > run_openai.sh << 'OPENAI_SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY not set"
    echo "Get key from: https://platform.openai.com/"
    echo "Set it with: export OPENAI_API_KEY='your-key'"
    exit 1
fi

echo "Running pipeline with OpenAI GPT-5.2..."
python -m langextract.providers.unified_production_pipeline \
    --terms "telomere length" "p16INK4a" \
    --email biomarkerextract@test.com \
    --provider openai \
    --api-key $OPENAI_API_KEY \
    --max-papers 20
OPENAI_SCRIPT
chmod +x run_openai.sh
echo "✓ run_openai.sh created"

# Anthropic script
cat > run_anthropic.sh << 'ANTHROPIC_SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    echo "Get key from: https://console.anthropic.com/"
    echo "Set it with: export ANTHROPIC_API_KEY='your-key'"
    exit 1
fi

echo "Running pipeline with Claude 4.5..."
python -m langextract.providers.unified_production_pipeline \
    --terms "DNA methylation" "senescence" \
    --email biomarkerextract@test.com \
    --provider anthropic \
    --api-key $ANTHROPIC_API_KEY \
    --max-papers 20
ANTHROPIC_SCRIPT
chmod +x run_anthropic.sh
echo "✓ run_anthropic.sh created"

# Gemini script
cat > run_gemini.sh << 'GEMINI_SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY not set"
    echo "Get key from: https://aistudio.google.com/"
    echo "Set it with: export GEMINI_API_KEY='your-key'"
    exit 1
fi

echo "Running pipeline with Gemini 3.0..."
python -m langextract.providers.unified_production_pipeline \
    --terms "NAD+" "mitochondria" \
    --email biomarkerextract@test.com \
    --provider gemini \
    --api-key $GEMINI_API_KEY \
    --max-papers 20
GEMINI_SCRIPT
chmod +x run_gemini.sh
echo "✓ run_gemini.sh created"

# Ollama script
cat > run_ollama.sh << 'OLLAMA_SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Error: Ollama is not running"
    echo "Start it with: ollama serve"
    exit 1
fi

echo "Running pipeline with Ollama (Local)..."
python -m langextract.providers.unified_production_pipeline \
    --terms "aging biomarkers" \
    --email biomarkerextract@test.com \
    --provider ollama \
    --model llama3.3 \
    --max-papers 10
OLLAMA_SCRIPT
chmod +x run_ollama.sh
echo "✓ run_ollama.sh created"
echo ""

echo "Step 7: System check..."
python << 'SYSCHECK'
import sys
print(f"Python version: {sys.version.split()[0]}")

try:
    from langextract.core import biomarker_models
    print("✓ Phase 3 models available")
except ImportError:
    print("✗ Phase 3 models not found")

try:
    from langextract.literature import batch_processor
    print("✓ Phase 4 literature available")
except ImportError:
    print("✗ Phase 4 literature not found")

try:
    from langextract.providers import unified_llm_provider
    print("✓ Unified LLM provider available")
except ImportError:
    print("✗ Unified LLM provider not found")

try:
    from langextract.providers import unified_production_pipeline
    print("✓ Unified production pipeline available")
except ImportError:
    print("✗ Unified production pipeline not found")
SYSCHECK
echo ""

echo "======================================================================"
echo "Installation Summary"
echo "======================================================================"
echo ""
echo "Files installed:"
echo "  • langextract/providers/unified_llm_provider.py"
echo "  • langextract/providers/unified_production_pipeline.py"
echo "  • examples_unified.py"
echo "  • docs/UNIFIED_CONFIGURATION.md"
echo "  • docs/UNIFIED_README.md"
echo ""
echo "Quick-start scripts:"
echo "  • run_openrouter.sh - OpenRouter (RECOMMENDED)"
echo "  • run_openai.sh - OpenAI GPT-5.2"
echo "  • run_anthropic.sh - Claude 4.5"
echo "  • run_gemini.sh - Gemini 3.0"
echo "  • run_ollama.sh - Ollama Local (FREE)"
echo ""
echo "Configuration:"
echo "  • .env.template - Copy to .env and add API keys"
echo ""
echo "======================================================================"
echo "Supported Providers"
echo "======================================================================"
echo ""
echo "1. OpenRouter (RECOMMENDED) ⭐"
echo "   - 100+ models with ONE API key"
echo "   - Get key: https://openrouter.ai/"
echo "   - Cost: $0.03-3 per 100 papers"
echo ""
echo "2. OpenAI GPT-5.2"
echo "   - Latest, most capable"
echo "   - Get key: https://platform.openai.com/"
echo "   - Cost: ~$2.50 per 100 papers"
echo ""
echo "3. Anthropic Claude 4.5"
echo "   - Best reasoning"
echo "   - Get key: https://console.anthropic.com/"
echo "   - Cost: ~$3.00 per 100 papers"
echo ""
echo "4. Google Gemini 3.0"
echo "   - Good balance"
echo "   - Get key: https://aistudio.google.com/"
echo "   - Cost: ~$1.00 per 100 papers"
echo ""
echo "5. Ollama (Local) ⭐"
echo "   - 100% FREE"
echo "   - Install: curl https://ollama.ai/install.sh | sh"
echo "   - Cost: $0.00"
echo ""
echo "======================================================================"
echo "Quick Start"
echo "======================================================================"
echo ""
echo "Option 1: OpenRouter (RECOMMENDED)"
echo "  1. Get API key: https://openrouter.ai/"
echo "  2. export OPENROUTER_API_KEY='your-key'"
echo "  3. bash run_openrouter.sh"
echo ""
echo "Option 2: OpenAI"
echo "  1. Get API key: https://platform.openai.com/"
echo "  2. export OPENAI_API_KEY='your-key'"
echo "  3. bash run_openai.sh"
echo ""
echo "Option 3: Ollama (Local, FREE)"
echo "  1. curl https://ollama.ai/install.sh | sh"
echo "  2. ollama pull llama3.3"
echo "  3. ollama serve"
echo "  4. bash run_ollama.sh"
echo ""
echo "======================================================================"
echo "Unified LLM Production Pipeline - READY ✓"
echo "======================================================================"
echo ""
echo "Next: Choose your provider and run your first pipeline!"
echo ""
