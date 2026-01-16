# ICPS-BSVA Electoral Workforce Survey Analysis

## Project Overview

This repository contains the data analysis pipeline and web dashboard for the **ICPS Electoral Workforce Survey** conducted in partnership with the **BSV Association (BSVA)**. The survey gathered feedback from electoral officials and experts across diverse jurisdictions to identify operational pain points in how temporary and permanent electoral staff are recruited, trained, retained, and evaluated.

## Business Context

### Partnership Background

The **International Centre for Parliamentary Studies (ICPS)** has significant market penetration and credibility within the global electoral community, with a member database of over 2,000 Electoral Commissioners and a general electoral database of over 6,000 contacts. ICPS provides this community with symposia, electoral awards, webinars, and commercial training solutions.

The **BSV Association** is exploring blockchain-based solutions for electoral workforce management challenges, including credential verification, training assurance, and workforce continuity.

### Project Evolution

This project evolved from an initial solution-oriented approach to a **problem-discovery methodology**. The key insight was that solution-oriented surveys that assume blockchain benefits without understanding actual operational needs are fundamentally flawed. The survey was reframed from "solution-testing" to "problem-discovery," prioritising genuine pain point identification before proposing technological solutions.

### Target Audience

- Approximately 6,000 electoral officials and experts worldwide
- Particular attention to young democracies in Africa with fundamental infrastructure constraints
- Election Management Bodies (EMBs) from various jurisdictions including South Africa, Philippines, United States, Dominica, and Canada

---

## Survey Data Structure

### Source Format

The raw data is a **SurveyMonkey export** with specific characteristics that must be handled during processing:

- **Row 1**: Question text (often truncated or split across merged cells)
- **Row 2**: Answer option labels for each column
- **Row 3+**: Response data

### Data Dimensions

- **Total columns**: ~213 (many questions split across multiple columns)
- **Response rows**: ~46 (including partial completions)
- **Complete responses**: ~25-30 with substantive data
- **Countries represented**: 20+ jurisdictions globally

### Column Structure Patterns

The SurveyMonkey format splits questions into multiple columns:

```
Single-select questions:
  Column: "Question text?"
  Values: Selected option text or empty

Multi-select questions (select all that apply):
  Columns: "Question text?", "", "", "" (one per option)
  Row 2: "Option A", "Option B", "Option C", "Option D"
  Values: Option text if selected, empty if not

Likert scale questions:
  Columns: "Question - Very unconfident", "Question - 2", "Question - 3", "Question - 4", "Question - Very Confident"
  Values: Selected rating or empty

Matrix questions:
  Columns: "Topic A - Rating 1", "Topic A - Rating 2", ..., "Topic B - Rating 1", ...
  Values: Selected rating or empty
```

### Key Question Areas (by column groups)

1. **Credential Verification** (cols ~10-27)
    - Fraud incidents (5-point scale: None to 20+)
    - Staff time spent (5-point scale: <5hrs to 100+hrs)
    - Primary challenges (multi-select, 8 options)

2. **Temporary Workforce** (cols ~28-48)
    - Workforce percentage (4 categories)
    - Time spent on activities (5 sub-questions, open numeric)
    - Worker composition percentages (new/returning/experienced)
    - Management challenges (multi-select, 8 options)

3. **Training Systems** (cols ~49-68)
    - Verification frequency (5-point scale)
    - Lost record handling (6 options)
    - Hours resolving issues (5-point scale)
    - System confidence (5-point Likert)

4. **Documentation** (cols ~69-95)
    - Methods used (multi-select: paper, digital, software, signatures)
    - Confidence ratings for 4 areas (5-point Likert each)
    - Open-ended challenges

5. **Data Synchronisation** (cols ~96-118)
    - Conflicting information frequency (5-point scale)
    - Provisional ballot tracking (6 options)
    - System-wide sync time (6 options)
    - System confidence (5-point Likert)

6. **Technology Infrastructure** (cols ~119-145)
    - Current tech levels for 4 areas (4-point scale each)
    - Infrastructure limitations (multi-select, 7 options)
    - Adoption barriers (open-ended)

7. **Workforce Retention** (cols ~146-175)
    - Return rate (4 categories)
    - Technologies explored (multi-select, 7 options)
    - Retention impact ratings for 3 interventions (4-point + don't know)
    - Worker interest in credentials (5 options)

8. **Priorities & Support** (cols ~176-195)
    - Top 3 operational priorities (open-ended)
    - External support ranking (7 options)
    - Implementation concerns (open-ended)
    - Single change suggestion (open-ended)

9. **Demographics** (cols ~196-213)
    - Country/Jurisdiction
    - Number of temporary workers
    - Elections managed annually
    - Follow-up interview willingness
    - Contact information

---

## Analysis Approach: Hybrid Methodology

### Why Hybrid?

The raw SurveyMonkey export format is not directly analysable. Multi-column encoding, mixed data types, and partial responses require programmatic cleaning before meaningful analysis. However, the rich qualitative data (open-ended responses) benefits from AI synthesis.

**Phase 1 (Python)**: Data cleaning, structuring, and quantitative analysis
**Phase 2 (Claude)**: Qualitative synthesis, narrative generation, and executive summary

### Phase 1: Python Data Processing

#### Step 1.1: Data Cleaning (`01_data_cleaning.py`)

Primary objectives:
- Parse the two-row header structure (question text + answer options)
- Consolidate multi-column questions into single meaningful columns
- Convert Likert scales to numeric values (1-5)
- Handle multi-select questions (create lists or binary columns)
- Extract and validate country/jurisdiction data
- Filter out partial responses (define completion threshold)
- Output clean CSV and JSON formats

Expected outputs:
- `data/processed/survey_clean.csv` - Flat, analysis-ready format
- `data/processed/survey_clean.json` - Structured for webapp consumption
- `data/processed/column_mapping.json` - Documentation of transformations

#### Step 1.2: Exploratory Analysis (`02_exploratory_analysis.py`)

Primary objectives:
- Response rate and completion analysis
- Summary statistics for each question area
- Distribution visualisations
- Missing data patterns
- Initial correlation exploration

Expected outputs:
- `analysis/outputs/summary_stats.json`
- `analysis/outputs/charts/` - PNG/SVG visualisations
- `analysis/outputs/completion_analysis.json`

#### Step 1.3: Segment Analysis (`03_segment_analysis.py`)

Primary objectives:
- Regional groupings (Africa, Asia-Pacific, Europe, Americas)
- Infrastructure maturity segmentation
- Pain point severity scoring
- Blockchain readiness assessment
- Pilot candidate identification and scoring

Expected outputs:
- `analysis/outputs/regional_comparison.json`
- `analysis/outputs/infrastructure_segments.json`
- `analysis/outputs/pilot_candidates.json`
- `analysis/outputs/pain_point_rankings.json`

### Phase 2: Qualitative Synthesis (Claude)

Once clean data is available, use Claude for:

#### Narrative Tasks
- Synthesise open-ended responses into themes
- Identify compelling quotes for presentations
- Write executive summary narrative
- Generate webinar talking points
- Create country/jurisdiction profiles

#### Input for Claude
- Cleaned JSON data
- Summary statistics
- Segment analysis outputs
- Raw open-ended responses (extracted and cleaned)

#### Expected Outputs
- `reports/executive_summary.md`
- `reports/key_findings.md`
- `reports/pilot_recommendations.md`
- `reports/webinar_script.md`

---

## Repository Structure

```
/
├── CLAUDE.md                          # This file - project context and instructions
├── REBUILD.md                         # Instructions for rebuilding the dashboard
├── rebuild.sh                         # Single-command pipeline script
├── data/
│   ├── raw/
│   │   └── Electoral_Workforce_Survey.csv    # Original SurveyMonkey export
│   └── processed/
│       ├── survey_clean.csv           # Cleaned flat format
│       ├── survey_clean.json          # Structured JSON for webapp
│       ├── column_mapping.json        # Transformation documentation
│       └── open_responses.json        # Extracted qualitative data
├── analysis/
│   ├── 01_data_cleaning.py
│   ├── 02_exploratory_analysis.py
│   ├── 03_segment_analysis.py
│   ├── utils/
│   │   ├── surveymonkey_parser.py     # Header parsing utilities
│   │   ├── likert_converter.py        # Scale conversion utilities
│   │   └── multiselect_handler.py     # Multi-select processing
│   └── outputs/
│       ├── summary_stats.json
│       ├── regional_comparison.json
│       ├── pilot_candidates.json
│       └── charts/
├── reports/
│   ├── executive_summary.md
│   ├── key_findings.md
│   └── pilot_recommendations.md
└── webapp/                            # Next.js + shadcn/ui dashboard
    ├── app/
    ├── components/
    └── lib/
```

---

## Technical Specifications

### Python Environment

```
python >= 3.10
pandas >= 2.0
numpy >= 1.24
matplotlib >= 3.7
seaborn >= 0.12
```

### Data Processing Guidelines

#### Likert Scale Encoding
```python
LIKERT_5_POINT = {
    'Very unconfident': 1,
    'Unconfident': 2,
    'Neutral': 3,
    'Confident': 4,
    'Very Confident': 5
}

LIKERT_IMPACT = {
    'No impact (0)': 0,
    'Slight impact (1)': 1,
    'Moderate impact (2)': 2,
    'Significant impact (3)': 3,
    "Don't know": None
}
```

#### Frequency Scale Encoding
```python
FREQUENCY_SCALE = {
    'Never': 0,
    'Rarely (1-5 times per election)': 1,
    'Sometimes (6-20 times per election)': 2,
    'Often (21-50 times per election)': 3,
    'Very often (more than 50 times per election)': 4
}
```

#### Regional Groupings
```python
REGIONS = {
    'Africa': ['Kenya', 'Uganda', 'Tanzania', 'Somaliland', 'Lesotho', 
               'Sierra Leone', 'Botswana', 'Nigeria', 'Mauritania', 'Zanzibar'],
    'Asia-Pacific': ['Pakistan', 'Maldives', 'Taiwan', 'Vanuatu', 'Bangladesh', 'Bhutan'],
    'Europe': ['Albania', 'Serbia', 'Lithuania', 'Armenia'],
    'Americas': ['United States', 'Suriname', 'Antigua & Barbuda']
}
```

### Webapp Technology Stack

- **Framework**: Next.js 14+ with App Router
- **UI Components**: shadcn/ui
- **Styling**: Tailwind CSS
- **Charts**: Recharts or similar
- **Data**: Static JSON imports (no backend required)

---

## Key Findings from Initial Research

### Universal Challenges Identified

1. **Administrative & Financial Overhead** - Significant strain managing temporary staffing logistics, long lead times, large staff volumes, heavy reliance on manual processes
2. **Inconsistent or Ad Hoc Training** - Decentralised training standards varying widely by jurisdiction
3. **Retention and Engagement Gaps** - Difficulty retaining trained workers between elections due to budget constraints
4. **Lack of Performance Feedback Mechanisms** - Pre/post-training assessments rarely formalised
5. **Youth Recruitment & Diversity** - Priority globally but lacking consistent follow-up mechanisms
6. **Digital Transition & Infrastructure Gaps** - Infrastructure barriers in regions with limited digital access
7. **Institutional Memory & Continuity** - Frequent rule changes diminishing value of returning staff

### Potential Blockchain Solutions (For Exploration)

- **Credentialing & Verification** - Tamper-proof storage of staff credentials and training completion
- **Token-Gated Access** - Role-specific training module access
- **Community Engagement** - Year-round engagement platforms between elections
- **Performance-Based Rewards** - Token incentives for participation and performance
- **Auditable Feedback** - Transparent record of training outcomes and evaluations

---

## Analysis Objectives

### Primary Goals

1. **Identify Pain Point Severity** - Rank operational challenges by impact and frequency across jurisdictions
2. **Segment Analysis** - Compare responses by region, organisation size, and infrastructure maturity
3. **Blockchain Readiness Assessment** - Determine which EMBs have sufficient infrastructure for pilot programs
4. **Pilot Candidate Identification** - Flag organisations showing both need and capability for blockchain solutions

### Key Metrics to Extract

- Response rates and completion patterns
- Pain point severity scores by category
- Infrastructure capability indicators
- Technology adoption readiness levels
- Regional and jurisdictional comparisons
- Correlation between challenges and potential blockchain benefits

### Pilot Candidate Scoring Framework

Score candidates on:
1. **Need** (0-10): Severity of pain points in areas blockchain could address
2. **Capability** (0-10): Infrastructure readiness (connectivity, devices, IT support)
3. **Willingness** (0-5): Interest in follow-up, technology exploration history
4. **Scale** (context): Size of workforce, elections managed

Ideal pilots: High need + adequate capability + expressed willingness

---

## Webapp Requirements

### Dashboard Features

1. **Executive Summary View** - High-level findings with key statistics
2. **Pain Point Explorer** - Interactive breakdown of challenges by category and region
3. **Jurisdiction Profiles** - Individual EMB/country analysis pages
4. **Blockchain Readiness Matrix** - Visual mapping of need vs capability
5. **Pilot Candidate List** - Filterable list of potential implementation partners

### Design Principles

- Clean, professional aesthetic suitable for government/institutional audiences
- Mobile-responsive design
- Accessible colour schemes and typography
- Export capabilities for reports and presentations
- No authentication required (internal use dashboard)

---

## Project Timeline Context

### Completed
- Survey design and methodology refinement
- Data collection phase
- Initial stakeholder interviews (South Africa, Philippines, US, Dominica, Canada)

### Current Phase
- Survey data analysis (this repository)
- Results visualisation
- Dashboard development

### Upcoming
- Executive summary for BSVA
- Strategic meeting to discuss findings
- Webinar presentation to ICPS electoral community
- Pilot candidate outreach

---

## Key Stakeholders

- **ICPS** - Tracy Capaldi-Drewett (Executive Vice President)
- **BSVA** - Asgeir Oskarsson, Vivek Chand
- **Buzzmint** - Charles Symons (technology partner)
- **Survey Respondents** - Electoral commissioners and officials globally

---

## Important Considerations

### Methodology Notes

- Survey design prioritised respondent burden - questions were refined rather than expanded
- Problem-discovery approach means we're looking for genuine pain points, not confirmation of blockchain benefits
- Many EMBs (especially in developing democracies) face basic infrastructure constraints that must be addressed before advanced technology solutions
- Results should inform whether blockchain is appropriate, not assume it is

### Presentation Context

The webinar proposal is titled **"Empowering the Election Workforce: Blockchain Solutions for Credential Verification, Training Assurance, and Workforce Continuity"**. The analysis should support a balanced presentation that:

1. Honestly represents the challenges identified
2. Acknowledges infrastructure limitations where they exist
3. Identifies genuinely suitable pilot candidates
4. Avoids overselling blockchain as a universal solution

### Data Sensitivity

- Survey responses may contain identifying information about specific EMBs
- Analysis outputs for public presentation should be appropriately aggregated
- Individual jurisdiction data should be handled with care
- Contact information fields should not be exposed in webapp or reports

---

## Working with This Repository

### Rebuilding the Dashboard

Use the automated pipeline to regenerate all analysis outputs and update the webapp:

```bash
# Full rebuild (runs Python scripts + copies JSON to webapp)
./rebuild.sh

# Full rebuild + build webapp for production
./rebuild.sh --build

# From webapp directory
npm run rebuild
```

The pipeline runs:
1. `01_data_cleaning.py` - Parses raw SurveyMonkey export
2. `02_exploratory_analysis.py` - Generates summary statistics
3. `03_segment_analysis.py` - Creates regional/pilot analysis
4. Copies 7 JSON files to `webapp/src/data/`

**Note:** `qualitative_synthesis.json` must be updated manually via Claude analysis of open-ended responses.

See `REBUILD.md` for full documentation.

### For Claude Code

**When working on Python analysis scripts:**
- Start with `01_data_cleaning.py` - this is foundational
- The SurveyMonkey format is tricky - pay attention to the two-row header
- Test transformations on a few rows before processing the full dataset
- Document all encoding decisions in `column_mapping.json`
- Generate intermediate outputs for review before proceeding

**When working on qualitative synthesis:**
- Wait until clean data is available from Phase 1
- Focus on the open-ended response fields for rich insights
- Pull specific quotes that illustrate key findings
- Maintain balanced tone - problem-discovery, not solution-selling

**When working on the webapp:**
- Use shadcn/ui components consistently
- Keep the interface clean and professional
- Ensure all visualisations are accessible
- Test with realistic data volumes
- Design for the primary audience: electoral officials and BSVA stakeholders

### Output Formats

Analysis scripts should produce:
- Summary statistics as JSON for webapp consumption
- Charts as PNG/SVG for presentations
- Markdown reports for documentation

---

## References

### Source Documents (in `/mnt/project/`)

- `BSVA_Proposal_Appendix_A__Preface_ICPS_Survey.pdf` - Key findings and blockchain solution mapping
- `Proposal_for_Initial_Project_for_BSVA.pdf` - Project scope and timeline
- `Empowering_the_Election_Workforce_with_BSV_Blockchain.pdf` - Challenge/solution framework presentation

### ICPS Resources

- Electoral Network: https://www.electoralnetwork.org/
- ICPS Main Site: https://www.parlicentre.org/