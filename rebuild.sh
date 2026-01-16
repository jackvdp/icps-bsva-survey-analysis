#!/bin/bash
set -e

echo "=== ICPS Survey Analysis Pipeline ==="
echo ""

# Activate Python environment
source venv/bin/activate

# Step 1: Data cleaning
echo "[1/3] Running data cleaning..."
python analysis/01_data_cleaning.py

# Step 2: Exploratory analysis
echo "[2/3] Running exploratory analysis..."
python analysis/02_exploratory_analysis.py

# Step 3: Segment analysis
echo "[3/3] Running segment analysis..."
python analysis/03_segment_analysis.py

# Step 4: Copy outputs to webapp
echo ""
echo "Copying JSON files to webapp/src/data/..."
cp data/processed/survey_clean.json webapp/src/data/
cp analysis/outputs/summary_stats.json webapp/src/data/
cp analysis/outputs/completion_analysis.json webapp/src/data/
cp analysis/outputs/regional_comparison.json webapp/src/data/
cp analysis/outputs/pilot_candidates.json webapp/src/data/
cp analysis/outputs/pain_point_rankings.json webapp/src/data/
cp analysis/outputs/infrastructure_segments.json webapp/src/data/

# Step 5: Build webapp (optional)
if [ "$1" == "--build" ]; then
  echo ""
  echo "Building webapp..."
  cd webapp && npm run build
fi

echo ""
echo "✓ Pipeline complete!"
echo ""
echo "NOTE: qualitative_synthesis.json must be updated manually if needed."
echo "      Run 'cd webapp && npm run dev' to preview the dashboard."
