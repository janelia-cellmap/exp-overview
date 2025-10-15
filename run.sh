#!/bin/bash
# Main execution script for experiment overview generation

set -e  # Exit on any error

echo "🔬 Experiment Overview Generator"
echo "==============================="

# Activate conda environment
echo "📦 Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate fly

# Set working directory
cd "$(dirname "$0")"
REPO_ROOT="$(pwd)"

echo "📂 Working directory: $REPO_ROOT"

# Check if required directories exist
echo "🔍 Checking directory structure..."
mkdir -p data/processed output/reports

# Generate the main overview CSV
echo "📊 Generating experiment overview..."
python scripts/generate_overview_csv.py

# Move output to correct location
if [ -f "auto_generated_overview.csv" ]; then
    mv auto_generated_overview.csv data/processed/
    echo "✅ Overview CSV generated: data/processed/auto_generated_overview.csv"
fi

if [ -f "comparison_report.md" ]; then
    mv comparison_report.md output/reports/
    echo "✅ Comparison report generated: output/reports/comparison_report.md"
fi

# Generate timeline if script exists
if [ -f "scripts/generate_timeline.py" ]; then
    echo "📈 Generating timeline visualization..."
    python scripts/generate_timeline.py
    echo "✅ Timeline generated: output/visualizations/"
fi

# Generate scores visualization if script exists
if [ -f "scripts/generate_scores.py" ]; then
    echo "🎯 Generating scores visualization..."
    python scripts/generate_scores.py
    echo "✅ Scores visualizations generated: output/visualizations/"
fi

# Summary
echo ""
echo "🎉 Experiment overview generation complete!"
echo ""
echo "📋 Generated files:"
echo "   📊 data/processed/auto_generated_overview.csv - Main experiment overview"
echo "   📝 output/reports/comparison_report.md - Data accuracy report"
echo "   📈 output/visualizations/ - HTML visualizations"
echo ""
echo "🔗 Quick access:"
echo "   View data: cat data/processed/auto_generated_overview.csv"
echo "   View report: cat output/reports/comparison_report.md"
echo "   Open viz: open output/visualizations/index.html"