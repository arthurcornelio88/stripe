#!/bin/bash

# Set Python path
export PYTHONPATH="$(pwd)"
echo "✅ PYTHONPATH set to $(pwd)"

# Detect environment
ENV=${ENV:-DEV}
ENV_FILE=".env.${ENV,,}"  # Lowercase (dev/prod)

# Check if env file exists
if [ -f "$ENV_FILE" ]; then
  echo "🔧 Loading environment variables from $ENV_FILE"
  export $(grep -v '^#' "$ENV_FILE" | xargs -d '\n')
  echo "✅ Environment variables loaded for ENV=$ENV"
else
  echo "❌ Environment file '$ENV_FILE' not found!"
  exit 1
fi
