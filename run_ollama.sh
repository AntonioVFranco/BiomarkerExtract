#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Error: Ollama is not running"
    echo "Install: curl https://ollama.ai/install.sh | sh"
    echo "Pull model: ollama pull llama3.3"
    echo "Start: ollama serve"
    exit 1
fi

echo "Running pipeline with Ollama (Local - FREE)..."
python -m langextract.providers.unified_production_pipeline \
    --terms "aging biomarkers" \
    --email biomarkerextract@test.com \
    --provider ollama \
    --model llama3.3 \
    --max-papers 10
