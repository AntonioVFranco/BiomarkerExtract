#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY not set"
    echo "Get key from: https://platform.openai.com/"
    exit 1
fi

echo "Running pipeline with OpenAI GPT-5.2..."
python -m langextract.providers.unified_production_pipeline \
    --terms "telomere length" "p16INK4a" \
    --email biomarkerextract@test.com \
    --provider openai \
    --api-key $OPENAI_API_KEY \
    --max-papers 20
