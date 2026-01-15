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
