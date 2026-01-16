"""
Electoral Workforce Survey Exploratory Analysis

Generates summary statistics, visualizations, and completion analysis
from the cleaned survey data.
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "outputs"
CHARTS_DIR = OUTPUT_DIR / "charts"

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Scale labels for readable outputs
FRAUD_LABELS = {0: 'None', 1: '1-5', 2: '6-10', 3: '11-20', 4: '20+'}
STAFF_TIME_LABELS = {1: '<5 hrs', 2: '5-20 hrs', 3: '21-50 hrs', 4: '51-100 hrs', 5: '100+ hrs'}
FREQUENCY_LABELS = {0: 'Never', 1: 'Rarely', 2: 'Sometimes', 3: 'Often', 4: 'Very Often'}
CONFIDENCE_LABELS = {1: 'Very Unconfident', 2: 'Unconfident', 3: 'Neutral', 4: 'Confident', 5: 'Very Confident'}
TECH_LEVEL_LABELS = {0: 'None', 1: 'Basic', 2: 'Moderate', 3: 'Advanced'}
WORKFORCE_PCT_LABELS = {1: '<25%', 2: '25-50%', 3: '51-75%', 4: '75%+'}
RETURN_RATE_LABELS = {1: '0-25%', 2: '26-50%', 3: '51-75%', 4: '76-100%'}
IMPACT_LABELS = {0: 'No Impact', 1: 'Slight', 2: 'Moderate', 3: 'Significant'}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the cleaned survey data and all responses."""
    csv_path = PROCESSED_DIR / "survey_clean.csv"
    df = pd.read_csv(csv_path)

    # Parse dates
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
    df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')

    # Load all responses (including incomplete) for raw count
    all_path = PROCESSED_DIR / "survey_all_responses.csv"
    df_all = pd.read_csv(all_path)

    return df, df_all


def parse_list_column(series: pd.Series) -> List[List[str]]:
    """Parse string representation of lists back to actual lists."""
    result = []
    for val in series:
        if pd.isna(val) or val == '':
            result.append([])
        elif isinstance(val, str):
            # Handle string representation of list
            if val.startswith('['):
                try:
                    # Clean up the string and parse
                    cleaned = val.replace("'", '"')
                    result.append(json.loads(cleaned))
                except:
                    result.append([])
            else:
                result.append([val])
        else:
            result.append([])
    return result


def calculate_response_stats(df: pd.DataFrame, df_all: pd.DataFrame) -> Dict[str, Any]:
    """Calculate overall response statistics."""
    stats = {
        'total_raw_responses': len(df_all),
        'total_responses': len(df),
        'date_range': {
            'earliest': str(df['start_date'].min()),
            'latest': str(df['end_date'].max()),
        },
        'completion': {
            'mean': round(df['completion_score'].mean(), 1),
            'median': round(df['completion_score'].median(), 1),
            'min': round(df['completion_score'].min(), 1),
            'max': round(df['completion_score'].max(), 1),
            'std': round(df['completion_score'].std(), 1),
        },
        'countries': {
            'unique_count': df['country'].nunique(),
            'list': df['country'].dropna().unique().tolist(),
        },
        'regions': df['region'].value_counts().to_dict(),
        'followup_willing': df['followup_willing'].value_counts().to_dict(),
    }
    return stats


def analyze_numeric_column(series: pd.Series, labels: Dict = None) -> Dict[str, Any]:
    """Analyze a numeric column and return statistics."""
    # Convert to numeric, coercing errors to NaN
    numeric_series = pd.to_numeric(series, errors='coerce')
    valid = numeric_series.dropna()

    if len(valid) == 0:
        return {'n': 0, 'missing': len(series)}

    stats = {
        'n': len(valid),
        'missing': len(series) - len(valid),
        'missing_pct': round((len(series) - len(valid)) / len(series) * 100, 1),
        'mean': round(float(valid.mean()), 2),
        'median': round(float(valid.median()), 2),
        'std': round(float(valid.std()), 2) if len(valid) > 1 else 0,
        'min': int(valid.min()),
        'max': int(valid.max()),
    }

    # Value counts with labels
    counts = valid.value_counts().sort_index()
    if labels:
        stats['distribution'] = {labels.get(int(k), str(int(k))): int(v) for k, v in counts.items()}
    else:
        stats['distribution'] = {str(int(k)): int(v) for k, v in counts.items()}

    return stats


def analyze_multiselect_column(series: pd.Series) -> Dict[str, Any]:
    """Analyze a multi-select column (lists of options)."""
    parsed = parse_list_column(series)

    # Count all selections
    all_selections = []
    responses_with_data = 0
    for selections in parsed:
        if selections:
            all_selections.extend(selections)
            responses_with_data += 1

    option_counts = Counter(all_selections)

    return {
        'n': responses_with_data,
        'missing': len(series) - responses_with_data,
        'missing_pct': round((len(series) - responses_with_data) / len(series) * 100, 1),
        'total_selections': len(all_selections),
        'avg_selections_per_response': round(len(all_selections) / max(responses_with_data, 1), 2),
        'option_counts': dict(option_counts.most_common()),
    }


def analyze_credential_verification(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze credential verification section."""
    return {
        'fraud_incidents': analyze_numeric_column(df['fraud_incidents'], FRAUD_LABELS),
        'verification_hours': analyze_numeric_column(df['credential_verification_hours'], STAFF_TIME_LABELS),
        'challenges': analyze_multiselect_column(df['credential_challenges']),
    }


def analyze_temporary_workforce(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze temporary workforce section."""
    return {
        'workforce_percentage': analyze_numeric_column(df['temp_workforce_percentage'], WORKFORCE_PCT_LABELS),
        'challenges': analyze_multiselect_column(df['workforce_challenges']),
    }


def analyze_training_systems(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze training systems section."""
    return {
        'verification_frequency': analyze_numeric_column(df['training_verification_frequency'], FREQUENCY_LABELS),
        'hours_resolving': analyze_numeric_column(df['hours_resolving_training'], STAFF_TIME_LABELS),
        'system_confidence': analyze_numeric_column(df['training_system_confidence'], CONFIDENCE_LABELS),
        'lost_record_handling': df['lost_record_handling'].value_counts().to_dict(),
    }


def analyze_documentation(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze documentation section."""
    confidence_cols = {
        'ballot_tracking': 'doc_confidence_tracking_ballot_movement',
        'recording_incidents': 'doc_confidence_recording_incidents',
        'audit_preparedness': 'doc_confidence_audit_preparedness',
        'legal_defensibility': 'doc_confidence_legal_defensibility',
    }

    confidence_stats = {}
    for name, col in confidence_cols.items():
        if col in df.columns:
            confidence_stats[name] = analyze_numeric_column(df[col], CONFIDENCE_LABELS)

    return {
        'methods': analyze_multiselect_column(df['documentation_methods']),
        'confidence': confidence_stats,
    }


def analyze_data_sync(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data synchronization section."""
    return {
        'conflicting_info_frequency': analyze_numeric_column(df['conflicting_info_frequency'], FREQUENCY_LABELS),
        'provisional_ballot_tracking': df['provisional_ballot_tracking'].value_counts().to_dict(),
        'sync_time': df['sync_time'].value_counts().to_dict(),
        'sync_confidence': analyze_numeric_column(df['sync_system_confidence'], CONFIDENCE_LABELS),
    }


def analyze_technology(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze technology infrastructure section."""
    tech_cols = {
        'recruitment': 'tech_level_worker_recruitment',
        'training': 'tech_level_training_delivery',
        'performance': 'tech_level_performance_tracking',
        'communication': 'tech_level_communication_systems',
    }

    tech_stats = {}
    for name, col in tech_cols.items():
        if col in df.columns:
            tech_stats[name] = analyze_numeric_column(df[col], TECH_LEVEL_LABELS)

    return {
        'levels': tech_stats,
        'limitations': analyze_multiselect_column(df['infrastructure_limitations']),
    }


def analyze_retention(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze workforce retention section."""
    # Find retention impact columns
    impact_cols = [col for col in df.columns if col.startswith('retention_impact_')
                   and 'requested' not in col and 'mentioned' not in col and 'discussed' not in col]

    impact_stats = {}
    for col in impact_cols[:3]:  # First 3 are the actual impact questions
        clean_name = col.replace('retention_impact_', '')[:50]
        impact_stats[clean_name] = analyze_numeric_column(df[col], IMPACT_LABELS)

    return {
        'return_rate': analyze_numeric_column(df['worker_return_rate'], RETURN_RATE_LABELS),
        'technologies_explored': analyze_multiselect_column(df['technologies_explored']),
        'retention_impact': impact_stats,
        'worker_interest': analyze_numeric_column(df['worker_interest_credentials'],
                                                   {1: 'Never Raised', 2: 'Rarely', 3: 'Occasionally', 4: 'Frequently'}),
    }


def analyze_external_support(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze external support needs."""
    return {
        'support_needed': analyze_multiselect_column(df['external_support_needed']),
    }


def calculate_missing_data_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a report on missing data patterns."""
    missing_report = {}

    for col in df.columns:
        if col in ['respondent_id', 'collector_id', 'start_date', 'end_date', 'country_raw']:
            continue

        missing_count = df[col].isna().sum()
        # Also count empty strings and 'nan' strings
        if df[col].dtype == 'object':
            empty_count = (df[col].astype(str).str.strip() == '').sum()
            missing_count = max(missing_count, empty_count)

        missing_pct = round(missing_count / len(df) * 100, 1)

        if missing_pct > 0:
            missing_report[col] = {
                'missing_count': int(missing_count),
                'missing_pct': missing_pct,
            }

    # Sort by missing percentage
    missing_report = dict(sorted(missing_report.items(), key=lambda x: x[1]['missing_pct'], reverse=True))

    return {
        'by_column': missing_report,
        'high_missing_columns': [col for col, info in missing_report.items() if info['missing_pct'] > 50],
        'moderate_missing_columns': [col for col, info in missing_report.items() if 25 < info['missing_pct'] <= 50],
    }


# =============================================================================
# Visualization Functions
# =============================================================================

def plot_regional_distribution(df: pd.DataFrame):
    """Create regional distribution pie chart."""
    fig, ax = plt.subplots(figsize=(10, 8))

    region_counts = df['region'].value_counts()
    colors = sns.color_palette("husl", len(region_counts))

    wedges, texts, autotexts = ax.pie(
        region_counts.values,
        labels=region_counts.index,
        autopct='%1.0f%%',
        colors=colors,
        explode=[0.02] * len(region_counts),
    )

    ax.set_title('Survey Responses by Region', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'regional_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_fraud_incidents(df: pd.DataFrame):
    """Create fraud incidents bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Convert to numeric first
    numeric_data = pd.to_numeric(df['fraud_incidents'], errors='coerce').dropna()
    counts = numeric_data.value_counts().sort_index()

    if len(counts) == 0:
        plt.close()
        return

    labels = [FRAUD_LABELS.get(int(k), str(int(k))) for k in counts.index]

    bars = ax.bar(labels, counts.values, color=sns.color_palette("husl", len(counts)))
    ax.bar_label(bars)

    ax.set_xlabel('Fraud Incidents (last 3 election cycles)')
    ax.set_ylabel('Number of Responses')
    ax.set_title('Credential Fraud Incidents Reported', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'fraud_incidents.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_confidence_comparison(df: pd.DataFrame):
    """Create confidence ratings comparison chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    confidence_data = {
        'Training System': pd.to_numeric(df['training_system_confidence'], errors='coerce').dropna(),
        'Sync System': pd.to_numeric(df['sync_system_confidence'], errors='coerce').dropna(),
        'Ballot Tracking': pd.to_numeric(df['doc_confidence_tracking_ballot_movement'], errors='coerce').dropna(),
        'Audit Prep': pd.to_numeric(df['doc_confidence_audit_preparedness'], errors='coerce').dropna(),
    }

    positions = range(len(confidence_data))
    means = [float(data.mean()) for data in confidence_data.values()]
    stds = [float(data.std()) if len(data) > 1 else 0 for data in confidence_data.values()]

    bars = ax.bar(positions, means, yerr=stds, capsize=5,
                  color=sns.color_palette("husl", len(confidence_data)))

    ax.set_xticks(positions)
    ax.set_xticklabels(confidence_data.keys(), rotation=15, ha='right')
    ax.set_ylabel('Confidence Score (1-5)')
    ax.set_title('System Confidence Ratings Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 5.5)
    ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, label='Neutral')

    # Add value labels
    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{mean:.1f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'confidence_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_tech_levels(df: pd.DataFrame):
    """Create technology levels comparison chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    tech_cols = {
        'Worker Recruitment': 'tech_level_worker_recruitment',
        'Training Delivery': 'tech_level_training_delivery',
        'Performance Tracking': 'tech_level_performance_tracking',
        'Communication': 'tech_level_communication_systems',
    }

    tech_data = {}
    for name, col in tech_cols.items():
        if col in df.columns:
            tech_data[name] = pd.to_numeric(df[col], errors='coerce').dropna()

    positions = range(len(tech_data))
    means = [float(data.mean()) for data in tech_data.values()]

    bars = ax.bar(positions, means, color=sns.color_palette("husl", len(tech_data)))

    ax.set_xticks(positions)
    ax.set_xticklabels(tech_data.keys(), rotation=15, ha='right')
    ax.set_ylabel('Technology Level (0-3)')
    ax.set_title('Technology Adoption by Function', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 3.5)

    # Add level labels on y-axis
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(['None', 'Basic', 'Moderate', 'Advanced'])

    # Add value labels
    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{mean:.1f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'tech_levels.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_infrastructure_limitations(df: pd.DataFrame):
    """Create infrastructure limitations horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(12, 8))

    limitations = analyze_multiselect_column(df['infrastructure_limitations'])
    counts = limitations['option_counts']

    if counts:
        # Sort by count
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items)

        # Truncate long labels
        labels = [l[:40] + '...' if len(l) > 40 else l for l in labels]

        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values, color=sns.color_palette("husl", len(labels)))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Number of Responses')
        ax.set_title('Infrastructure Limitations Reported', fontsize=14, fontweight='bold')
        ax.bar_label(bars, padding=3)

        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'infrastructure_limitations.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_credential_challenges(df: pd.DataFrame):
    """Create credential challenges horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(12, 8))

    challenges = analyze_multiselect_column(df['credential_challenges'])
    counts = challenges['option_counts']

    if counts:
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items)

        labels = [l[:45] + '...' if len(l) > 45 else l for l in labels]

        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values, color=sns.color_palette("husl", len(labels)))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Number of Responses')
        ax.set_title('Credential System Challenges', fontsize=14, fontweight='bold')
        ax.bar_label(bars, padding=3)

        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'credential_challenges.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_workforce_challenges(df: pd.DataFrame):
    """Create workforce challenges horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(12, 8))

    challenges = analyze_multiselect_column(df['workforce_challenges'])
    counts = challenges['option_counts']

    if counts:
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items)

        labels = [l[:45] + '...' if len(l) > 45 else l for l in labels]

        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values, color=sns.color_palette("husl", len(labels)))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Number of Responses')
        ax.set_title('Temporary Workforce Management Challenges', fontsize=14, fontweight='bold')
        ax.bar_label(bars, padding=3)

        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'workforce_challenges.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_external_support_needs(df: pd.DataFrame):
    """Create external support needs horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    support = analyze_multiselect_column(df['external_support_needed'])
    counts = support['option_counts']

    if counts:
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items)

        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values, color=sns.color_palette("husl", len(labels)))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Number of Responses')
        ax.set_title('External Support Needs', fontsize=14, fontweight='bold')
        ax.bar_label(bars, padding=3)

        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'external_support_needs.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_technologies_explored(df: pd.DataFrame):
    """Create technologies explored horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    tech = analyze_multiselect_column(df['technologies_explored'])
    counts = tech['option_counts']

    if counts:
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items)

        labels = [l[:40] + '...' if len(l) > 40 else l for l in labels]

        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values, color=sns.color_palette("husl", len(labels)))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Number of Responses')
        ax.set_title('Technologies Explored by EMBs', fontsize=14, fontweight='bold')
        ax.bar_label(bars, padding=3)

        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'technologies_explored.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_regional_comparison_confidence(df: pd.DataFrame):
    """Create regional comparison of confidence scores."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Convert to numeric first
    df_numeric = df.copy()
    df_numeric['training_system_confidence'] = pd.to_numeric(df['training_system_confidence'], errors='coerce')
    df_numeric['sync_system_confidence'] = pd.to_numeric(df['sync_system_confidence'], errors='coerce')

    # Calculate mean confidence by region
    confidence_by_region = df_numeric.groupby('region').agg({
        'training_system_confidence': 'mean',
        'sync_system_confidence': 'mean',
    }).dropna()

    x = range(len(confidence_by_region))
    width = 0.35

    bars1 = ax.bar([i - width/2 for i in x], confidence_by_region['training_system_confidence'],
                   width, label='Training System', color='steelblue')
    bars2 = ax.bar([i + width/2 for i in x], confidence_by_region['sync_system_confidence'],
                   width, label='Sync System', color='coral')

    ax.set_xticks(x)
    ax.set_xticklabels(confidence_by_region.index, rotation=15, ha='right')
    ax.set_ylabel('Mean Confidence Score (1-5)')
    ax.set_title('System Confidence by Region', fontsize=14, fontweight='bold')
    ax.legend()
    ax.set_ylim(0, 5.5)
    ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'regional_confidence.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_worker_return_rate(df: pd.DataFrame):
    """Create worker return rate distribution chart."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Convert to numeric first
    numeric_data = pd.to_numeric(df['worker_return_rate'], errors='coerce').dropna()
    counts = numeric_data.value_counts().sort_index()

    if len(counts) == 0:
        plt.close()
        return

    labels = [RETURN_RATE_LABELS.get(int(k), str(int(k))) for k in counts.index]

    bars = ax.bar(labels, counts.values, color=sns.color_palette("husl", len(counts)))
    ax.bar_label(bars)

    ax.set_xlabel('Percentage of Workers Returning')
    ax.set_ylabel('Number of Responses')
    ax.set_title('Temporary Worker Return Rate Distribution', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'worker_return_rate.png', dpi=150, bbox_inches='tight')
    plt.close()


def main():
    """Main analysis pipeline."""
    print("Loading cleaned survey data...")
    df, df_all = load_data()
    print(f"Loaded {len(df)} complete responses ({len(df_all)} total)")

    # ==========================================================================
    # Generate Summary Statistics
    # ==========================================================================
    print("\nGenerating summary statistics...")

    summary_stats = {
        'response_overview': calculate_response_stats(df, df_all),
        'credential_verification': analyze_credential_verification(df),
        'temporary_workforce': analyze_temporary_workforce(df),
        'training_systems': analyze_training_systems(df),
        'documentation': analyze_documentation(df),
        'data_synchronization': analyze_data_sync(df),
        'technology_infrastructure': analyze_technology(df),
        'workforce_retention': analyze_retention(df),
        'external_support': analyze_external_support(df),
    }

    # Save summary stats
    stats_path = OUTPUT_DIR / "summary_stats.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {stats_path}")

    # ==========================================================================
    # Generate Completion Analysis
    # ==========================================================================
    print("\nGenerating completion analysis...")

    completion_analysis = {
        'completion_stats': {
            'mean': round(df['completion_score'].mean(), 1),
            'median': round(df['completion_score'].median(), 1),
            'std': round(df['completion_score'].std(), 1),
            'min': round(df['completion_score'].min(), 1),
            'max': round(df['completion_score'].max(), 1),
        },
        'missing_data': calculate_missing_data_report(df),
        'completion_by_region': df.groupby('region')['completion_score'].mean().round(1).to_dict(),
    }

    completion_path = OUTPUT_DIR / "completion_analysis.json"
    with open(completion_path, 'w', encoding='utf-8') as f:
        json.dump(completion_analysis, f, indent=2, ensure_ascii=False)
    print(f"Saved: {completion_path}")

    # ==========================================================================
    # Generate Visualizations
    # ==========================================================================
    print("\nGenerating visualizations...")

    plot_regional_distribution(df)
    print("  - regional_distribution.png")

    plot_fraud_incidents(df)
    print("  - fraud_incidents.png")

    plot_confidence_comparison(df)
    print("  - confidence_comparison.png")

    plot_tech_levels(df)
    print("  - tech_levels.png")

    plot_infrastructure_limitations(df)
    print("  - infrastructure_limitations.png")

    plot_credential_challenges(df)
    print("  - credential_challenges.png")

    plot_workforce_challenges(df)
    print("  - workforce_challenges.png")

    plot_external_support_needs(df)
    print("  - external_support_needs.png")

    plot_technologies_explored(df)
    print("  - technologies_explored.png")

    plot_regional_comparison_confidence(df)
    print("  - regional_confidence.png")

    plot_worker_return_rate(df)
    print("  - worker_return_rate.png")

    # ==========================================================================
    # Print Key Findings
    # ==========================================================================
    print("\n" + "="*60)
    print("KEY FINDINGS SUMMARY")
    print("="*60)

    print(f"\n1. RESPONSE OVERVIEW")
    print(f"   - Total responses: {len(df)}")
    print(f"   - Countries: {df['country'].nunique()}")
    regions = [str(r) for r in df['region'].dropna().unique()]
    print(f"   - Regions: {', '.join(regions)}")

    print(f"\n2. CREDENTIAL VERIFICATION")
    fraud = pd.to_numeric(df['fraud_incidents'], errors='coerce').dropna()
    print(f"   - {(fraud == 0).sum()} EMBs report zero fraud incidents")
    print(f"   - {(fraud > 0).sum()} EMBs report at least some fraud incidents")

    print(f"\n3. TEMPORARY WORKFORCE")
    workforce = pd.to_numeric(df['temp_workforce_percentage'], errors='coerce').dropna()
    high_temp = (workforce >= 4).sum()  # 75%+ temporary
    print(f"   - {high_temp} EMBs have 75%+ temporary workforce")

    print(f"\n4. SYSTEM CONFIDENCE (scale 1-5)")
    training_conf = pd.to_numeric(df['training_system_confidence'], errors='coerce').mean()
    sync_conf = pd.to_numeric(df['sync_system_confidence'], errors='coerce').mean()
    print(f"   - Training system: {training_conf:.1f}")
    print(f"   - Sync system: {sync_conf:.1f}")

    print(f"\n5. TECHNOLOGY ADOPTION (scale 0-3)")
    for name, col in [('Recruitment', 'tech_level_worker_recruitment'),
                      ('Training', 'tech_level_training_delivery'),
                      ('Performance', 'tech_level_performance_tracking')]:
        if col in df.columns:
            val = pd.to_numeric(df[col], errors='coerce').mean()
            print(f"   - {name}: {val:.1f}")

    print(f"\n6. TOP INFRASTRUCTURE LIMITATIONS")
    infra = analyze_multiselect_column(df['infrastructure_limitations'])
    for item, count in list(infra['option_counts'].items())[:3]:
        print(f"   - {item}: {count} responses")

    print(f"\n7. WORKER INTEREST IN CREDENTIALS")
    interest_numeric = pd.to_numeric(df['worker_interest_credentials'], errors='coerce')
    interest = interest_numeric.value_counts()
    # Use .get() with default 0 for values 3 (Occasionally) and 4 (Frequently)
    total_interested = int(interest.loc[interest.index == 3].sum()) + int(interest.loc[interest.index == 4].sum())
    print(f"   - {total_interested} EMBs report worker interest (occasional or frequent)")

    print(f"\n8. EXTERNAL SUPPORT NEEDS")
    support = analyze_multiselect_column(df['external_support_needed'])
    for item, count in list(support['option_counts'].items())[:3]:
        print(f"   - {item}: {count} responses")

    print("\n" + "="*60)
    print(f"Charts saved to: {CHARTS_DIR}")
    print(f"Stats saved to: {OUTPUT_DIR}")
    print("="*60)

    return df, summary_stats


if __name__ == "__main__":
    df, stats = main()
