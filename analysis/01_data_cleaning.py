"""
Electoral Workforce Survey Data Cleaning Script

Parses SurveyMonkey export format and transforms into analysis-ready data.
Handles two-row headers, multi-select questions, Likert scales, and more.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "survey_responses.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Ensure output directory exists
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Scale Encodings (from CLAUDE.md)
# =============================================================================

LIKERT_5_POINT_CONFIDENCE = {
    'Very unconfident': 1,
    'Unconfident': 2,
    'Neutral': 3,
    'Confident': 4,
    'Very Confident': 5,
    '2': 2,
    '3': 3,
    '4': 4,
}

LIKERT_IMPACT = {
    'No impact (0)': 0,
    'Slight impact (1)': 1,
    'Moderate impact (2)': 2,
    'Significant impact (3)': 3,
    "Don't know": None,
}

FREQUENCY_SCALE = {
    'Never': 0,
    'Rarely (1-5 times per election)': 1,
    'Sometimes (6-20 times per election)': 2,
    'Often (21-50 times per election)': 3,
    'Very often (more than 50 times per election)': 4,
}

FREQUENCY_INCIDENTS = {
    'Never': 0,
    'Rarely (1-10 incidents per election)': 1,
    'Sometimes (11-50 incidents per election)': 2,
    'Often (51-200 incidents per election)': 3,
    'Very often (more than 200 incidents per election)': 4,
}

FRAUD_INCIDENTS = {
    'None': 0,
    '1-5 incidents': 1,
    '6-10 incidents': 2,
    '11-20 incidents': 3,
    'More than 20 incidents': 4,
}

STAFF_TIME = {
    'Less than 5 total hours': 1,
    '5-20 hours': 2,
    '21-50 hours': 3,
    '51-100 hours': 4,
    'More than 100 hours': 5,
}

HOURS_RESOLVING = {
    'Less than 10 hours': 1,
    '10-50 hours': 2,
    '51-100 hours': 3,
    '101-200 hours': 4,
    'More than 200 hours': 5,
}

WORKFORCE_PERCENTAGE = {
    'Less than 25%': 1,
    '25-50%': 2,
    '51-75%': 3,
    'More than 75%': 4,
}

RETURN_RATE = {
    '0-25%': 1,
    '26-50%': 2,
    '51-75%': 3,
    '76-100%': 4,
}

TECH_LEVEL = {
    'None': 0,
    'Basic': 1,
    'Moderate': 2,
    'Advanced': 3,
}

WORKER_INTEREST = {
    'Yes, frequently requested': 4,
    'Yes, occasionally mentioned': 3,
    'Rarely discussed': 2,
    'Never raised': 1,
    "Don't know": None,
}

# Regional groupings
REGIONS = {
    'Africa': ['Kenya', 'Uganda', 'Tanzania', 'Tanzania (Zanzibar)', 'Somaliland', 'Lesotho',
               'Sierra Leone', 'Botswana', 'Nigeria', 'Mauritania', 'Zanzibar', 'Ethiopia',
               'NIGERIA', 'UGANDA', 'LESOTHO'],
    'Asia-Pacific': ['Pakistan', 'Maldives', 'Taiwan', 'Vanuatu', 'Bangladesh',
                     'Bhutan', 'TAIWAN', 'India'],
    'Europe': ['Albania', 'Serbia', 'Lithuania', 'Armenia', 'Europe and Eurasia region',
               'Europe/Eurasia (Regional)'],
    'Americas': ['United States', 'Suriname', 'Antigua & Barbuda', 'Antigua',
                 'Antigua 🇦🇬 and Barbuda'],
}


def load_raw_data() -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Load raw CSV and extract the two-row header structure."""
    # Read CSV without treating first row as header
    df_raw = pd.read_csv(RAW_DATA_PATH, header=None, dtype=str)

    # Extract header rows
    question_row = df_raw.iloc[0].fillna('').tolist()
    option_row = df_raw.iloc[1].fillna('').tolist()

    # Get response data (skip header rows)
    df_responses = df_raw.iloc[2:].reset_index(drop=True)

    return df_responses, question_row, option_row


def create_column_mapping(question_row: List[str], option_row: List[str]) -> Dict[int, Dict[str, Any]]:
    """
    Create a mapping of column indices to their question context.
    Handles multi-column questions by propagating question text.
    """
    mapping = {}
    current_question = ""

    for i, (q, o) in enumerate(zip(question_row, option_row)):
        # If there's a question, update current question
        if q.strip():
            current_question = q.strip()

        mapping[i] = {
            'question': current_question,
            'option': o.strip() if o else '',
            'original_col': i,
        }

    return mapping


def identify_question_groups(column_mapping: Dict) -> Dict[str, List[int]]:
    """Group column indices by their parent question."""
    groups = {}

    for col_idx, info in column_mapping.items():
        question = info['question']
        if question:
            if question not in groups:
                groups[question] = []
            groups[question].append(col_idx)

    return groups


def find_columns_by_pattern(column_mapping: Dict, pattern: str) -> List[int]:
    """Find column indices where question or option contains pattern."""
    matches = []
    pattern_lower = pattern.lower()
    for col_idx, info in column_mapping.items():
        if pattern_lower in info['question'].lower() or pattern_lower in info['option'].lower():
            matches.append(col_idx)
    return matches


def find_question_columns(question_groups: Dict, pattern: str) -> List[int]:
    """Find columns for a question matching the pattern."""
    pattern_lower = pattern.lower()
    for question, cols in question_groups.items():
        if pattern_lower in question.lower():
            return cols
    return []


def is_multiselect_question(question: str) -> bool:
    """Determine if a question is multi-select based on its text."""
    multiselect_indicators = [
        'Select all that apply',
        'Select up to',
        'select all',
        'Rank top',
    ]
    return any(ind.lower() in question.lower() for ind in multiselect_indicators)


def is_likert_confidence(options: List[str]) -> bool:
    """Check if options represent a Likert confidence scale."""
    confidence_terms = ['unconfident', 'confident', 'neutral']
    return any(term in ' '.join(options).lower() for term in confidence_terms)


def is_likert_impact(options: List[str]) -> bool:
    """Check if options represent an impact scale."""
    return any('impact' in opt.lower() for opt in options)


def process_multiselect(df: pd.DataFrame, col_indices: List[int],
                        column_mapping: Dict, question: str) -> pd.Series:
    """
    Process multi-select questions by combining selected options into a list.
    Returns a Series with lists of selected options.
    """
    result = []

    for _, row in df.iterrows():
        selected = []
        for col_idx in col_indices:
            value = row.iloc[col_idx]
            if pd.notna(value) and str(value).strip():
                option = column_mapping[col_idx]['option']
                # Use the option text if available, otherwise use the value
                if option:
                    selected.append(option)
                else:
                    selected.append(str(value).strip())
        result.append(selected if selected else None)

    return pd.Series(result)


def process_likert_matrix(df: pd.DataFrame, col_indices: List[int],
                          column_mapping: Dict, scale_map: Dict) -> Dict[str, pd.Series]:
    """
    Process Likert matrix questions (e.g., confidence ratings for multiple items).
    Returns a dict of Series, one per sub-item.
    """
    results = {}

    # Group columns by their sub-item (extracted from option text)
    sub_items = {}
    for col_idx in col_indices:
        option = column_mapping[col_idx]['option']
        if ' - ' in option:
            parts = option.rsplit(' - ', 1)
            item_name = parts[0].strip()
            rating_text = parts[1].strip() if len(parts) > 1 else option
        else:
            item_name = option
            rating_text = option

        if item_name not in sub_items:
            sub_items[item_name] = []
        sub_items[item_name].append((col_idx, rating_text))

    # Process each sub-item
    for item_name, cols in sub_items.items():
        if not item_name:
            continue

        values = []
        for _, row in df.iterrows():
            found_value = None
            for col_idx, rating_text in cols:
                cell_value = row.iloc[col_idx]
                if pd.notna(cell_value) and str(cell_value).strip():
                    # Try to map the value using the scale
                    for scale_key, scale_val in scale_map.items():
                        if scale_key in rating_text or scale_key in str(cell_value):
                            found_value = scale_val
                            break
                    # If not found in scale, try numeric conversion
                    if found_value is None:
                        try:
                            found_value = int(str(cell_value).strip())
                        except ValueError:
                            found_value = cell_value
                    break
            values.append(found_value)

        clean_name = item_name.replace(' ', '_').lower()
        results[clean_name] = pd.Series(values)

    return results


def process_single_select(df: pd.DataFrame, col_indices: List[int],
                          column_mapping: Dict, scale_map: Optional[Dict] = None) -> pd.Series:
    """Process single-select questions, optionally mapping to numeric scale."""
    values = []

    for _, row in df.iterrows():
        found_value = None
        for col_idx in col_indices:
            cell_value = row.iloc[col_idx]
            if pd.notna(cell_value) and str(cell_value).strip():
                cell_str = str(cell_value).strip()

                # Try to map using scale if provided
                if scale_map:
                    for scale_key, scale_val in scale_map.items():
                        if scale_key.lower() == cell_str.lower() or scale_key in cell_str:
                            found_value = scale_val
                            break

                # If no scale match, use raw value
                if found_value is None:
                    found_value = cell_str
                break

        values.append(found_value)

    return pd.Series(values)


def clean_country_name(country: str) -> str:
    """Standardize country names."""
    if pd.isna(country):
        return None

    country = str(country).strip()

    # Standardization mappings
    mappings = {
        'TAIWAN': 'Taiwan',
        'UGANDA': 'Uganda',
        'LESOTHO': 'Lesotho',
        'NIGERIA': 'Nigeria',
        'NIGERIA / AFRICA': 'Nigeria',
        'nigeria': 'Nigeria',
        'Antigua 🇦🇬 and Barbuda': 'Antigua & Barbuda',
        'Antigua': 'Antigua & Barbuda',
        'Antigua ': 'Antigua & Barbuda',
        'Mauritanie': 'Mauritania',
        'Europe and Eurasia region': 'Europe/Eurasia (Regional)',
        'Established Country legal system approximately': 'Ethiopia',
        'Karnataka': 'India',
        'Zanzibar': 'Tanzania (Zanzibar)',
    }

    return mappings.get(country, country)


def get_region(country: str) -> Optional[str]:
    """Get region for a country."""
    if pd.isna(country):
        return None

    country_clean = clean_country_name(country)

    for region, countries in REGIONS.items():
        if country_clean in countries or country in countries:
            return region

    return 'Other'


def calculate_completion_score(row: pd.Series) -> float:
    """Calculate what percentage of the survey was completed."""
    non_empty = row.apply(lambda x: pd.notna(x) and str(x).strip() != '')
    return non_empty.sum() / len(row) * 100


def main():
    """Main data cleaning pipeline."""
    print("Loading raw survey data...")
    df_responses, question_row, option_row = load_raw_data()

    print(f"Loaded {len(df_responses)} response rows")
    print(f"Found {len(question_row)} columns")

    # Create column mapping
    print("\nCreating column mapping...")
    column_mapping = create_column_mapping(question_row, option_row)
    question_groups = identify_question_groups(column_mapping)

    print(f"Identified {len(question_groups)} question groups")

    # Initialize cleaned data dictionary
    cleaned_data = {}

    # ==========================================================================
    # Process Metadata Columns (0-8)
    # ==========================================================================
    print("\nProcessing metadata columns...")

    cleaned_data['respondent_id'] = df_responses.iloc[:, 0]
    cleaned_data['collector_id'] = df_responses.iloc[:, 1]
    cleaned_data['start_date'] = pd.to_datetime(df_responses.iloc[:, 2], errors='coerce')
    cleaned_data['end_date'] = pd.to_datetime(df_responses.iloc[:, 3], errors='coerce')

    # ==========================================================================
    # Process Credential Verification Questions
    # ==========================================================================
    print("Processing credential verification questions...")

    # Fraud incidents (cols 9-13)
    fraud_cols = [i for i in range(9, 14) if i < len(df_responses.columns)]
    cleaned_data['fraud_incidents'] = process_single_select(
        df_responses, fraud_cols, column_mapping, FRAUD_INCIDENTS
    )

    # Staff time on verification (cols 14-18)
    time_cols = [i for i in range(14, 19) if i < len(df_responses.columns)]
    cleaned_data['credential_verification_hours'] = process_single_select(
        df_responses, time_cols, column_mapping, STAFF_TIME
    )

    # Primary challenges with credentials (cols 19-27, multi-select)
    challenge_cols = [i for i in range(19, 28) if i < len(df_responses.columns)]
    cleaned_data['credential_challenges'] = process_multiselect(
        df_responses, challenge_cols, column_mapping, "credential challenges"
    )

    # ==========================================================================
    # Process Temporary Workforce Questions
    # ==========================================================================
    print("Processing temporary workforce questions...")

    # Workforce percentage (cols 28-31)
    workforce_cols = [i for i in range(28, 32) if i < len(df_responses.columns)]
    cleaned_data['temp_workforce_percentage'] = process_single_select(
        df_responses, workforce_cols, column_mapping, WORKFORCE_PERCENTAGE
    )

    # Time spent on activities (cols 32-36) - open numeric, keep as text
    activity_names = ['recruitment_onboarding', 'training_coordination',
                      'deployment_scheduling', 'payroll_processing', 'offboarding']
    for i, name in enumerate(activity_names):
        col_idx = 32 + i
        if col_idx < len(df_responses.columns):
            cleaned_data[f'hours_{name}'] = df_responses.iloc[:, col_idx]

    # Worker composition (cols 37-40)
    composition_names = ['new_workers_pct', 'returning_workers_pct',
                         'experienced_workers_pct', 'unknown_workers_pct']
    for i, name in enumerate(composition_names):
        col_idx = 37 + i
        if col_idx < len(df_responses.columns):
            cleaned_data[name] = df_responses.iloc[:, col_idx]

    # Workforce management challenges (cols 41-49, multi-select)
    mgmt_challenge_cols = [i for i in range(41, 50) if i < len(df_responses.columns)]
    cleaned_data['workforce_challenges'] = process_multiselect(
        df_responses, mgmt_challenge_cols, column_mapping, "workforce challenges"
    )

    # ==========================================================================
    # Process Training Systems Questions
    # ==========================================================================
    print("Processing training systems questions...")

    # Training verification frequency (cols 50-54)
    training_freq_cols = [i for i in range(50, 55) if i < len(df_responses.columns)]
    cleaned_data['training_verification_frequency'] = process_single_select(
        df_responses, training_freq_cols, column_mapping, FREQUENCY_SCALE
    )

    # Lost record handling (cols 55-60)
    lost_record_cols = [i for i in range(55, 61) if i < len(df_responses.columns)]
    cleaned_data['lost_record_handling'] = process_single_select(
        df_responses, lost_record_cols, column_mapping
    )

    # Hours resolving training issues (cols 61-65)
    hours_resolve_cols = [i for i in range(61, 66) if i < len(df_responses.columns)]
    cleaned_data['hours_resolving_training'] = process_single_select(
        df_responses, hours_resolve_cols, column_mapping, HOURS_RESOLVING
    )

    # Training system confidence (cols 66-70)
    training_conf_cols = [i for i in range(66, 71) if i < len(df_responses.columns)]
    cleaned_data['training_system_confidence'] = process_single_select(
        df_responses, training_conf_cols, column_mapping, LIKERT_5_POINT_CONFIDENCE
    )

    # ==========================================================================
    # Process Documentation Questions
    # ==========================================================================
    print("Processing documentation questions...")

    # Documentation methods (cols 71-75, multi-select)
    doc_method_cols = [i for i in range(71, 76) if i < len(df_responses.columns)]
    cleaned_data['documentation_methods'] = process_multiselect(
        df_responses, doc_method_cols, column_mapping, "documentation methods"
    )

    # Documentation confidence ratings (cols 76-95, matrix)
    # These are split into: ballot_tracking, recording_incidents, audit_prep, legal_defensibility
    doc_conf_cols = list(range(76, 96))
    doc_matrix = process_likert_matrix(
        df_responses, doc_conf_cols, column_mapping, LIKERT_5_POINT_CONFIDENCE
    )
    for key, series in doc_matrix.items():
        cleaned_data[f'doc_confidence_{key}'] = series

    # Documentation challenges (col 96, open-ended)
    if 96 < len(df_responses.columns):
        cleaned_data['documentation_challenges_text'] = df_responses.iloc[:, 96]

    # ==========================================================================
    # Process Data Synchronisation Questions
    # ==========================================================================
    print("Processing data synchronisation questions...")

    # Conflicting information frequency (cols 97-101)
    conflict_freq_cols = [i for i in range(97, 102) if i < len(df_responses.columns)]
    cleaned_data['conflicting_info_frequency'] = process_single_select(
        df_responses, conflict_freq_cols, column_mapping, FREQUENCY_INCIDENTS
    )

    # Provisional ballot tracking (cols 102-107)
    prov_ballot_cols = [i for i in range(102, 108) if i < len(df_responses.columns)]
    cleaned_data['provisional_ballot_tracking'] = process_single_select(
        df_responses, prov_ballot_cols, column_mapping
    )

    # Sync time (cols 108-113)
    sync_time_cols = [i for i in range(108, 114) if i < len(df_responses.columns)]
    cleaned_data['sync_time'] = process_single_select(
        df_responses, sync_time_cols, column_mapping
    )

    # Sync system confidence (cols 114-118)
    sync_conf_cols = [i for i in range(114, 119) if i < len(df_responses.columns)]
    cleaned_data['sync_system_confidence'] = process_single_select(
        df_responses, sync_conf_cols, column_mapping, LIKERT_5_POINT_CONFIDENCE
    )

    # ==========================================================================
    # Process Technology Infrastructure Questions
    # ==========================================================================
    print("Processing technology infrastructure questions...")

    # Technology levels (cols 119-134, matrix: recruitment, training, performance, communication)
    tech_level_cols = list(range(119, 135))
    tech_matrix = process_likert_matrix(
        df_responses, tech_level_cols, column_mapping, TECH_LEVEL
    )
    for key, series in tech_matrix.items():
        cleaned_data[f'tech_level_{key}'] = series

    # Infrastructure limitations (cols 135-141, multi-select)
    infra_limit_cols = [i for i in range(135, 142) if i < len(df_responses.columns)]
    cleaned_data['infrastructure_limitations'] = process_multiselect(
        df_responses, infra_limit_cols, column_mapping, "infrastructure limitations"
    )

    # Technology adoption barriers (col 142, open-ended)
    if 142 < len(df_responses.columns):
        cleaned_data['tech_adoption_barriers_text'] = df_responses.iloc[:, 142]

    # ==========================================================================
    # Process Workforce Retention Questions
    # ==========================================================================
    print("Processing workforce retention questions...")

    # Return rate (cols 143-146)
    return_rate_cols = [i for i in range(143, 147) if i < len(df_responses.columns)]
    cleaned_data['worker_return_rate'] = process_single_select(
        df_responses, return_rate_cols, column_mapping, RETURN_RATE
    )

    # Technologies explored (cols 147-154, multi-select)
    tech_explored_cols = [i for i in range(147, 155) if i < len(df_responses.columns)]
    cleaned_data['technologies_explored'] = process_multiselect(
        df_responses, tech_explored_cols, column_mapping, "technologies explored"
    )

    # Retention impact ratings (cols 155-169, matrix for portable creds, badges, service records)
    retention_impact_cols = list(range(155, 170))
    retention_matrix = process_likert_matrix(
        df_responses, retention_impact_cols, column_mapping, LIKERT_IMPACT
    )
    for key, series in retention_matrix.items():
        cleaned_data[f'retention_impact_{key}'] = series

    # Worker interest in credentials (cols 170-174)
    interest_cols = [i for i in range(170, 175) if i < len(df_responses.columns)]
    cleaned_data['worker_interest_credentials'] = process_single_select(
        df_responses, interest_cols, column_mapping, WORKER_INTEREST
    )

    # ==========================================================================
    # Process Priorities & Support Questions
    # ==========================================================================
    print("Processing priorities and support questions...")

    # Top 3 priorities (cols 175-177, open-ended)
    for i, label in enumerate(['priority_1', 'priority_2', 'priority_3']):
        col_idx = 175 + i
        if col_idx < len(df_responses.columns):
            cleaned_data[label] = df_responses.iloc[:, col_idx]

    # External support ranking (cols 178-184, multi-select/ranking)
    support_cols = [i for i in range(178, 185) if i < len(df_responses.columns)]
    cleaned_data['external_support_needed'] = process_multiselect(
        df_responses, support_cols, column_mapping, "external support"
    )

    # Implementation concerns (col 185, open-ended)
    if 185 < len(df_responses.columns):
        cleaned_data['implementation_concerns_text'] = df_responses.iloc[:, 185]

    # Single change suggestion (col 186, open-ended)
    if 186 < len(df_responses.columns):
        cleaned_data['single_change_suggestion_text'] = df_responses.iloc[:, 186]

    # ==========================================================================
    # Process Demographics (using dynamic column detection)
    # ==========================================================================
    print("Processing demographics...")

    # Find Country/Jurisdiction column
    country_cols = find_question_columns(question_groups, "Country/Jurisdiction")
    if country_cols:
        country_col = country_cols[0]
        cleaned_data['country_raw'] = df_responses.iloc[:, country_col]
        cleaned_data['country'] = cleaned_data['country_raw'].apply(clean_country_name)
        cleaned_data['region'] = cleaned_data['country'].apply(get_region)
        print(f"  Found country at column {country_col}")

    # Find Number of temporary workers column
    temp_workers_cols = find_question_columns(question_groups, "Approximate number of temporary workers")
    if temp_workers_cols:
        temp_col = temp_workers_cols[0]
        cleaned_data['temp_workers_count'] = df_responses.iloc[:, temp_col]
        print(f"  Found temp workers count at column {temp_col}")

    # Find Elections managed annually column
    elections_cols = find_question_columns(question_groups, "Number of elections managed annually")
    if elections_cols:
        elections_col = elections_cols[0]
        cleaned_data['elections_annually'] = df_responses.iloc[:, elections_col]
        print(f"  Found elections annually at column {elections_col}")

    # Find Follow-up interview willingness columns
    followup_cols = find_question_columns(question_groups, "Would you be willing to participate")
    if followup_cols:
        cleaned_data['followup_willing'] = process_single_select(
            df_responses, followup_cols, column_mapping
        )
        print(f"  Found followup at columns {followup_cols}")

    # ==========================================================================
    # Create DataFrame and Calculate Completion
    # ==========================================================================
    print("\nCreating cleaned DataFrame...")
    df_clean = pd.DataFrame(cleaned_data)

    # Calculate completion score for each respondent
    df_clean['completion_score'] = df_responses.apply(calculate_completion_score, axis=1)

    # Filter out very incomplete responses (less than 15% complete)
    print(f"Total responses: {len(df_clean)}")
    df_complete = df_clean[df_clean['completion_score'] >= 15].copy()
    print(f"Responses with >= 15% completion: {len(df_complete)}")

    # ==========================================================================
    # Extract Open-Ended Responses
    # ==========================================================================
    print("\nExtracting open-ended responses...")
    open_ended_cols = [col for col in df_clean.columns if col.endswith('_text')]
    open_responses = df_complete[['respondent_id', 'country'] + open_ended_cols].copy()

    # Add priority columns
    priority_cols = ['priority_1', 'priority_2', 'priority_3']
    for col in priority_cols:
        if col in df_complete.columns:
            open_responses[col] = df_complete[col]

    # ==========================================================================
    # Save Outputs
    # ==========================================================================
    print("\nSaving cleaned data...")

    # Save cleaned CSV (complete responses only)
    csv_path = PROCESSED_DIR / "survey_clean.csv"
    df_complete.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")

    # Save full data CSV (including partial responses)
    csv_all_path = PROCESSED_DIR / "survey_all_responses.csv"
    df_clean.to_csv(csv_all_path, index=False)
    print(f"Saved: {csv_all_path}")

    # Save JSON for webapp
    json_path = PROCESSED_DIR / "survey_clean.json"

    # Convert DataFrame to JSON-serializable format
    def convert_for_json(obj):
        if isinstance(obj, (pd.Timestamp, np.datetime64)):
            return str(obj) if pd.notna(obj) else None
        if isinstance(obj, (np.integer, np.floating)):
            return int(obj) if pd.notna(obj) else None
        if isinstance(obj, float) and np.isnan(obj):
            return None
        if pd.isna(obj):
            return None
        return obj

    json_data = []
    for _, row in df_complete.iterrows():
        record = {}
        for col in df_complete.columns:
            val = row[col]
            if isinstance(val, list):
                record[col] = val
            else:
                record[col] = convert_for_json(val)
        json_data.append(record)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {json_path}")

    # Save column mapping documentation
    mapping_path = PROCESSED_DIR / "column_mapping.json"

    # Convert column mapping to more readable format
    mapping_doc = {
        'question_groups': {},
        'scale_encodings': {
            'likert_confidence': LIKERT_5_POINT_CONFIDENCE,
            'likert_impact': LIKERT_IMPACT,
            'frequency': FREQUENCY_SCALE,
            'fraud_incidents': FRAUD_INCIDENTS,
            'staff_time': STAFF_TIME,
            'hours_resolving': HOURS_RESOLVING,
            'workforce_percentage': WORKFORCE_PERCENTAGE,
            'return_rate': RETURN_RATE,
            'tech_level': TECH_LEVEL,
            'worker_interest': WORKER_INTEREST,
        },
        'regions': REGIONS,
        'cleaned_columns': list(df_clean.columns),
    }

    for question, cols in question_groups.items():
        if question.strip():
            mapping_doc['question_groups'][question[:100]] = {
                'columns': cols,
                'is_multiselect': is_multiselect_question(question),
            }

    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(mapping_doc, f, indent=2, ensure_ascii=False)
    print(f"Saved: {mapping_path}")

    # Save open-ended responses
    open_path = PROCESSED_DIR / "open_responses.json"
    open_records = []
    for _, row in open_responses.iterrows():
        record = {}
        for col in open_responses.columns:
            val = row[col]
            if pd.notna(val) and str(val).strip():
                record[col] = convert_for_json(val)
        if len(record) > 2:  # Has more than just ID and country
            open_records.append(record)

    with open(open_path, 'w', encoding='utf-8') as f:
        json.dump(open_records, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {open_path}")

    # ==========================================================================
    # Print Summary Statistics
    # ==========================================================================
    print("\n" + "="*60)
    print("DATA CLEANING SUMMARY")
    print("="*60)
    print(f"\nTotal responses loaded: {len(df_clean)}")
    print(f"Complete responses (>=15%): {len(df_complete)}")
    print(f"Columns in cleaned data: {len(df_clean.columns)}")

    print(f"\nCountries represented: {df_complete['country'].nunique()}")
    print(f"Country breakdown:")
    for country in df_complete['country'].dropna().unique():
        count = len(df_complete[df_complete['country'] == country])
        print(f"  - {country}: {count}")

    print(f"\nRegional breakdown:")
    for region in df_complete['region'].dropna().unique():
        count = len(df_complete[df_complete['region'] == region])
        print(f"  - {region}: {count}")

    print(f"\nCompletion score statistics:")
    print(f"  Mean: {df_complete['completion_score'].mean():.1f}%")
    print(f"  Median: {df_complete['completion_score'].median():.1f}%")
    print(f"  Min: {df_complete['completion_score'].min():.1f}%")
    print(f"  Max: {df_complete['completion_score'].max():.1f}%")

    return df_clean, df_complete


if __name__ == "__main__":
    df_all, df_complete = main()