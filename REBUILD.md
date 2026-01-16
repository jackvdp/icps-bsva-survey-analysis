# Rebuilding the Dashboard

This document explains how to update the dashboard when raw survey data changes.

## Quick Start

```bash
# From project root:
./rebuild.sh

# Or from webapp directory:
npm run rebuild
```

## Full Process

### 1. Update Raw Data

Place the new SurveyMonkey export at:
```
data/raw/survey_responses.csv
```

### 2. Run the Pipeline

```bash
./rebuild.sh
```

This runs:
1. `01_data_cleaning.py` - Parses and cleans the raw CSV
2. `02_exploratory_analysis.py` - Generates summary statistics
3. `03_segment_analysis.py` - Creates regional and pilot candidate analysis
4. Copies all JSON outputs to `webapp/src/data/`

### 3. (Optional) Build for Production

```bash
./rebuild.sh --build
```

This runs the full pipeline and then builds the Next.js webapp.

### 4. Preview the Dashboard

```bash
cd webapp && npm run dev
```

Open http://localhost:3000 to view the updated dashboard.

## Updating Qualitative Synthesis

The file `webapp/src/data/qualitative_synthesis.json` is **not** updated by the rebuild script. This file contains AI-synthesised analysis of open-ended responses and must be updated manually:

1. Review the cleaned open-ended responses in `data/processed/open_responses.json`
2. Use Claude or similar to synthesise themes and insights
3. Update `webapp/src/data/qualitative_synthesis.json` with the new analysis

## Available Commands

| Command | Description |
|---------|-------------|
| `./rebuild.sh` | Run pipeline, copy files to webapp |
| `./rebuild.sh --build` | Run pipeline + build webapp |
| `npm run rebuild` | Same as `./rebuild.sh` (from webapp dir) |
| `npm run rebuild:build` | Same as `./rebuild.sh --build` (from webapp dir) |

## Output Files

The pipeline generates and copies these files to `webapp/src/data/`:

| File | Description |
|------|-------------|
| `survey_clean.json` | Cleaned survey responses |
| `summary_stats.json` | Aggregate statistics |
| `completion_analysis.json` | Response completion rates |
| `regional_comparison.json` | Analysis by region |
| `pilot_candidates.json` | Scored pilot candidate list |
| `pain_point_rankings.json` | Ranked operational challenges |
| `infrastructure_segments.json` | Infrastructure maturity groupings |

## Troubleshooting

**Python environment not found:**
Ensure you have a virtual environment at `venv/` with required packages installed.

**Missing raw data file:**
Place the SurveyMonkey export at `data/raw/survey_responses.csv`.

**Webapp build fails:**
Run `cd webapp && npm install` to ensure dependencies are installed.
