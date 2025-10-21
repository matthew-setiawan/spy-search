#!/bin/bash

# Script to update all hardcoded localhost references in frontend
# This replaces localhost:8000 with environment variable

API_URL='${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}'

echo "Updating frontend URLs..."

# Update all TypeScript/TSX files in frontend/src
find frontend/src -name "*.ts" -o -name "*.tsx" | while read file; do
    if grep -q "http://localhost:8000" "$file"; then
        echo "Updating $file"
        sed -i "s|http://localhost:8000|$API_URL|g" "$file"
    fi
done

echo "Frontend URLs updated!"
echo "Make sure to set VITE_API_BASE_URL environment variable in your deployment."
