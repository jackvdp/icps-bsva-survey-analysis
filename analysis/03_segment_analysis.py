"""
Electoral Workforce Survey Segment Analysis

Performs regional comparisons, infrastructure segmentation, pain point scoring,
and pilot candidate identification for blockchain solutions.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "outputs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    """Load the cleaned survey data."""
    csv_path = PROCESSED_DIR / "survey_clean.csv"
    df = pd.read_csv(csv_path)
    return df


def safe_numeric(series: pd.Series) -> pd.Series:
    """Convert series to numeric, coercing errors to NaN."""
    return pd.to_numeric(series, errors='coerce')


def parse_list_column(val) -> List[str]:
    """Parse a string representation of a list."""
    if pd.isna(val) or val == '':
        return []
    if isinstance(val, str):
        if val.startswith('['):
            try:
                cleaned = val.replace("'", '"')
                return json.loads(cleaned)
            except:
                return []
        return [val]
    return []


def clean_for_json(obj):
    """Recursively clean NaN/NaT values from data structures for JSON serialization."""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    elif pd.isna(obj):
        return None
    return obj


# =============================================================================
# Regional Comparison Analysis
# =============================================================================

def calculate_regional_comparison(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comprehensive regional comparison statistics."""
    regions = df['region'].dropna().unique()
    comparison = {}

    for region in regions:
        region_df = df[df['region'] == region]
        n = len(region_df)

        if n == 0:
            continue

        # Calculate mean scores for key metrics
        metrics = {
            'response_count': n,
            'countries': region_df['country'].dropna().unique().tolist(),

            # Credential verification
            'fraud_incidents_mean': safe_numeric(region_df['fraud_incidents']).mean(),
            'verification_hours_mean': safe_numeric(region_df['credential_verification_hours']).mean(),

            # Workforce
            'temp_workforce_pct_mean': safe_numeric(region_df['temp_workforce_percentage']).mean(),
            'worker_return_rate_mean': safe_numeric(region_df['worker_return_rate']).mean(),

            # System confidence
            'training_confidence_mean': safe_numeric(region_df['training_system_confidence']).mean(),
            'sync_confidence_mean': safe_numeric(region_df['sync_system_confidence']).mean(),

            # Technology levels
            'tech_recruitment_mean': safe_numeric(region_df['tech_level_worker_recruitment']).mean(),
            'tech_training_mean': safe_numeric(region_df['tech_level_training_delivery']).mean(),
            'tech_performance_mean': safe_numeric(region_df['tech_level_performance_tracking']).mean(),
            'tech_communication_mean': safe_numeric(region_df['tech_level_communication_systems']).mean(),

            # Completion
            'avg_completion_score': region_df['completion_score'].mean(),

            # Follow-up willingness
            'followup_willing_count': (region_df['followup_willing'] == 'Yes').sum(),
            'followup_willing_pct': (region_df['followup_willing'] == 'Yes').sum() / n * 100 if n > 0 else 0,
        }

        # Round numeric values
        for key, val in metrics.items():
            if isinstance(val, (int, float)):
                if pd.isna(val):
                    metrics[key] = None
                else:
                    metrics[key] = round(val, 2)

        # Infrastructure limitations breakdown
        limitations_count = {}
        for val in region_df['infrastructure_limitations']:
            for item in parse_list_column(val):
                if item and item != 'Open-Ended Response':
                    limitations_count[item] = limitations_count.get(item, 0) + 1
        metrics['top_infrastructure_limitations'] = dict(
            sorted(limitations_count.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        # Credential challenges breakdown
        challenges_count = {}
        for val in region_df['credential_challenges']:
            for item in parse_list_column(val):
                if item and 'Less than' not in item and item != 'Other':
                    challenges_count[item] = challenges_count.get(item, 0) + 1
        metrics['top_credential_challenges'] = dict(
            sorted(challenges_count.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        # Technologies explored
        tech_count = {}
        for val in region_df['technologies_explored']:
            for item in parse_list_column(val):
                if item and item not in ['None of the above', 'Other']:
                    tech_count[item] = tech_count.get(item, 0) + 1
        metrics['technologies_explored'] = dict(
            sorted(tech_count.items(), key=lambda x: x[1], reverse=True)
        )

        comparison[region] = metrics

    return comparison


# =============================================================================
# Infrastructure Maturity Segmentation
# =============================================================================

def calculate_infrastructure_score(row: pd.Series) -> Optional[float]:
    """
    Calculate infrastructure maturity score (0-10) based on:
    - Technology levels (0-3 scale each, 4 dimensions)
    - Infrastructure limitations (penalty for each)
    """
    # Technology levels (max 12 points -> normalized to 6)
    tech_cols = [
        'tech_level_worker_recruitment',
        'tech_level_training_delivery',
        'tech_level_performance_tracking',
        'tech_level_communication_systems',
    ]

    tech_scores = []
    for col in tech_cols:
        val = pd.to_numeric(row.get(col), errors='coerce')
        if pd.notna(val):
            tech_scores.append(val)

    if not tech_scores:
        return None

    # Average tech level (0-3) normalized to 0-6
    avg_tech = sum(tech_scores) / len(tech_scores)
    tech_component = (avg_tech / 3) * 6

    # Infrastructure limitations penalty (max -4 points)
    limitations = parse_list_column(row.get('infrastructure_limitations', ''))
    severe_limitations = [
        'Unreliable electricity',
        'Limited internet connectivity',
        'Lack of computers/devices',
        'Insufficient IT support',
    ]
    limitation_penalty = sum(1 for l in limitations if l in severe_limitations)
    limitation_component = max(0, 4 - limitation_penalty)

    return round(tech_component + limitation_component, 2)


def segment_by_infrastructure(df: pd.DataFrame) -> Dict[str, Any]:
    """Segment respondents by infrastructure maturity."""
    df = df.copy()
    df['infrastructure_score'] = df.apply(calculate_infrastructure_score, axis=1)

    # Define segments
    segments = {
        'advanced': {'min': 7, 'max': 10, 'respondents': []},
        'moderate': {'min': 4, 'max': 7, 'respondents': []},
        'basic': {'min': 0, 'max': 4, 'respondents': []},
    }

    for _, row in df.iterrows():
        score = row['infrastructure_score']
        if pd.isna(score):
            continue

        country = row['country']
        if pd.isna(country):
            continue

        entry = {
            'country': country,
            'region': row['region'],
            'score': score,
            'tech_recruitment': pd.to_numeric(row.get('tech_level_worker_recruitment'), errors='coerce'),
            'tech_training': pd.to_numeric(row.get('tech_level_training_delivery'), errors='coerce'),
            'followup_willing': row.get('followup_willing'),
        }

        if score >= 7:
            segments['advanced']['respondents'].append(entry)
        elif score >= 4:
            segments['moderate']['respondents'].append(entry)
        else:
            segments['basic']['respondents'].append(entry)

    # Calculate segment statistics
    for segment_name, segment_data in segments.items():
        respondents = segment_data['respondents']
        segment_data['count'] = len(respondents)
        if respondents:
            segment_data['avg_score'] = round(
                sum(r['score'] for r in respondents) / len(respondents), 2
            )
            segment_data['countries'] = list(set(r['country'] for r in respondents))
            segment_data['regions'] = dict(pd.Series([r['region'] for r in respondents]).value_counts())
        else:
            segment_data['avg_score'] = None
            segment_data['countries'] = []
            segment_data['regions'] = {}

    return {
        'segments': segments,
        'score_distribution': {
            'mean': round(df['infrastructure_score'].mean(), 2) if df['infrastructure_score'].notna().any() else None,
            'median': round(df['infrastructure_score'].median(), 2) if df['infrastructure_score'].notna().any() else None,
            'min': round(df['infrastructure_score'].min(), 2) if df['infrastructure_score'].notna().any() else None,
            'max': round(df['infrastructure_score'].max(), 2) if df['infrastructure_score'].notna().any() else None,
        },
    }


# =============================================================================
# Pain Point Severity Scoring
# =============================================================================

def calculate_pain_point_scores(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate pain point severity scores for different operational areas.
    Higher scores = more severe pain points.
    """
    pain_points = {}

    # 1. Credential Verification Pain Points
    credential_scores = []
    for _, row in df.iterrows():
        score = 0
        components = []

        # Fraud incidents (0-4 scale, high = more pain)
        fraud = pd.to_numeric(row.get('fraud_incidents'), errors='coerce')
        if pd.notna(fraud):
            score += fraud * 2  # Weight: 2x
            components.append(f"fraud:{fraud}")

        # Verification hours (1-5 scale, high = more pain)
        hours = pd.to_numeric(row.get('credential_verification_hours'), errors='coerce')
        if pd.notna(hours):
            score += (hours - 1) * 1.5  # Weight: 1.5x, normalized
            components.append(f"hours:{hours}")

        # Challenges count
        challenges = parse_list_column(row.get('credential_challenges', ''))
        challenges = [c for c in challenges if c and 'No significant' not in c and 'Less than' not in c]
        score += len(challenges) * 1
        components.append(f"challenges:{len(challenges)}")

        if components:
            credential_scores.append({'country': row['country'], 'score': round(score, 2)})

    pain_points['credential_verification'] = {
        'scores': sorted(credential_scores, key=lambda x: x['score'], reverse=True),
        'avg_score': round(sum(s['score'] for s in credential_scores) / len(credential_scores), 2) if credential_scores else 0,
        'max_score': max(s['score'] for s in credential_scores) if credential_scores else 0,
    }

    # 2. Temporary Workforce Pain Points
    workforce_scores = []
    for _, row in df.iterrows():
        score = 0

        # High temp workforce percentage (4 = 75%+, indicates dependency)
        temp_pct = pd.to_numeric(row.get('temp_workforce_percentage'), errors='coerce')
        if pd.notna(temp_pct):
            score += temp_pct * 1.5

        # Low return rate (inverted: low return = high pain)
        return_rate = pd.to_numeric(row.get('worker_return_rate'), errors='coerce')
        if pd.notna(return_rate):
            score += (5 - return_rate) * 1.5

        # Workforce challenges count
        challenges = parse_list_column(row.get('workforce_challenges', ''))
        challenges = [c for c in challenges if c and c != 'Other' and 'None' not in c]
        score += len(challenges) * 1

        if score > 0:
            workforce_scores.append({'country': row['country'], 'score': round(score, 2)})

    pain_points['temporary_workforce'] = {
        'scores': sorted(workforce_scores, key=lambda x: x['score'], reverse=True),
        'avg_score': round(sum(s['score'] for s in workforce_scores) / len(workforce_scores), 2) if workforce_scores else 0,
        'max_score': max(s['score'] for s in workforce_scores) if workforce_scores else 0,
    }

    # 3. Training Systems Pain Points
    training_scores = []
    for _, row in df.iterrows():
        score = 0

        # Verification frequency issues (high = more problems)
        freq = pd.to_numeric(row.get('training_verification_frequency'), errors='coerce')
        if pd.notna(freq):
            score += freq * 2

        # Hours resolving issues (high = more pain)
        hours = pd.to_numeric(row.get('hours_resolving_training'), errors='coerce')
        if pd.notna(hours):
            score += hours * 1.5

        # Low confidence (inverted: 5-score)
        confidence = pd.to_numeric(row.get('training_system_confidence'), errors='coerce')
        if pd.notna(confidence):
            score += (5 - confidence) * 1.5

        if score > 0:
            training_scores.append({'country': row['country'], 'score': round(score, 2)})

    pain_points['training_systems'] = {
        'scores': sorted(training_scores, key=lambda x: x['score'], reverse=True),
        'avg_score': round(sum(s['score'] for s in training_scores) / len(training_scores), 2) if training_scores else 0,
        'max_score': max(s['score'] for s in training_scores) if training_scores else 0,
    }

    # 4. Data Synchronization Pain Points
    sync_scores = []
    for _, row in df.iterrows():
        score = 0

        # Conflicting info frequency (high = more problems)
        freq = pd.to_numeric(row.get('conflicting_info_frequency'), errors='coerce')
        if pd.notna(freq):
            score += freq * 2

        # Low sync confidence (inverted)
        confidence = pd.to_numeric(row.get('sync_system_confidence'), errors='coerce')
        if pd.notna(confidence):
            score += (5 - confidence) * 1.5

        # No real-time sync
        sync_time = row.get('sync_time')
        if pd.notna(sync_time) and 'Instantly' not in str(sync_time):
            score += 2
        if pd.notna(sync_time) and "don't have" in str(sync_time).lower():
            score += 3

        if score > 0:
            sync_scores.append({'country': row['country'], 'score': round(score, 2)})

    pain_points['data_synchronization'] = {
        'scores': sorted(sync_scores, key=lambda x: x['score'], reverse=True),
        'avg_score': round(sum(s['score'] for s in sync_scores) / len(sync_scores), 2) if sync_scores else 0,
        'max_score': max(s['score'] for s in sync_scores) if sync_scores else 0,
    }

    # 5. Infrastructure Pain Points
    infra_scores = []
    for _, row in df.iterrows():
        score = 0

        # Count severe limitations
        limitations = parse_list_column(row.get('infrastructure_limitations', ''))
        severe = ['Unreliable electricity', 'Limited internet connectivity',
                  'Lack of computers/devices', 'Insufficient IT support', 'Budget constraints']
        for lim in limitations:
            if lim in severe:
                score += 2

        # Low tech levels (inverted)
        for col in ['tech_level_worker_recruitment', 'tech_level_training_delivery',
                    'tech_level_performance_tracking', 'tech_level_communication_systems']:
            level = pd.to_numeric(row.get(col), errors='coerce')
            if pd.notna(level):
                score += (3 - level) * 0.5

        if score > 0:
            infra_scores.append({'country': row['country'], 'score': round(score, 2)})

    pain_points['infrastructure'] = {
        'scores': sorted(infra_scores, key=lambda x: x['score'], reverse=True),
        'avg_score': round(sum(s['score'] for s in infra_scores) / len(infra_scores), 2) if infra_scores else 0,
        'max_score': max(s['score'] for s in infra_scores) if infra_scores else 0,
    }

    # Overall ranking by area
    pain_points['area_ranking'] = sorted(
        [
            {'area': 'credential_verification', 'avg_severity': pain_points['credential_verification']['avg_score']},
            {'area': 'temporary_workforce', 'avg_severity': pain_points['temporary_workforce']['avg_score']},
            {'area': 'training_systems', 'avg_severity': pain_points['training_systems']['avg_score']},
            {'area': 'data_synchronization', 'avg_severity': pain_points['data_synchronization']['avg_score']},
            {'area': 'infrastructure', 'avg_severity': pain_points['infrastructure']['avg_score']},
        ],
        key=lambda x: x['avg_severity'],
        reverse=True
    )

    return pain_points


# =============================================================================
# Pilot Candidate Scoring
# =============================================================================

def calculate_pilot_scores(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Score potential pilot candidates based on:
    - Need (0-10): Severity of pain points in blockchain-addressable areas
    - Capability (0-10): Infrastructure readiness
    - Willingness (0-5): Interest in follow-up, technology exploration
    - Scale: Contextual info about workforce size
    """
    candidates = []

    for _, row in df.iterrows():
        country = row.get('country')
        if pd.isna(country):
            continue

        # ----- NEED SCORE (0-10) -----
        # Pain points that blockchain could address:
        # - Credential verification issues
        # - Training record verification
        # - Worker tracking across elections
        need_score = 0
        need_components = []

        # Credential issues (fraud + verification time + challenges)
        fraud = pd.to_numeric(row.get('fraud_incidents'), errors='coerce')
        if pd.notna(fraud) and fraud > 0:
            need_score += min(fraud, 3)  # Max 3 points
            need_components.append(f"fraud_incidents:{fraud}")

        hours = pd.to_numeric(row.get('credential_verification_hours'), errors='coerce')
        if pd.notna(hours) and hours > 1:
            need_score += min((hours - 1) * 0.5, 1.5)  # Max 1.5 points
            need_components.append(f"verification_hours:{hours}")

        challenges = parse_list_column(row.get('credential_challenges', ''))
        relevant_challenges = [c for c in challenges if any(x in c.lower() for x in
                              ['centralised', 'verification', 'fraud', 'remote'])]
        need_score += min(len(relevant_challenges) * 0.5, 1.5)  # Max 1.5 points
        if relevant_challenges:
            need_components.append(f"challenges:{len(relevant_challenges)}")

        # Training verification issues
        training_freq = pd.to_numeric(row.get('training_verification_frequency'), errors='coerce')
        if pd.notna(training_freq) and training_freq > 1:
            need_score += min(training_freq * 0.5, 1.5)  # Max 1.5 points
            need_components.append(f"training_freq:{training_freq}")

        # Low system confidence (need for improvement)
        train_conf = pd.to_numeric(row.get('training_system_confidence'), errors='coerce')
        if pd.notna(train_conf) and train_conf < 4:
            need_score += (4 - train_conf) * 0.5  # Max 1.5 points
            need_components.append(f"low_train_conf:{train_conf}")

        # Worker retention issues (blockchain credentials could help)
        interest = pd.to_numeric(row.get('worker_interest_credentials'), errors='coerce')
        if pd.notna(interest) and interest >= 3:
            need_score += 1  # Bonus for expressed interest
            need_components.append(f"worker_interest:{interest}")

        need_score = min(round(need_score, 2), 10)

        # ----- CAPABILITY SCORE (0-10) -----
        capability_score = calculate_infrastructure_score(row)
        if capability_score is None:
            capability_score = 5  # Default middle score if no data

        capability_components = []

        # Check for severe limitations that would prevent blockchain adoption
        limitations = parse_list_column(row.get('infrastructure_limitations', ''))
        blockers = ['Unreliable electricity', 'Limited internet connectivity']
        blocker_count = sum(1 for l in limitations if l in blockers)
        if blocker_count > 0:
            capability_components.append(f"blockers:{blocker_count}")

        # Bonus for existing tech exploration
        tech_explored = parse_list_column(row.get('technologies_explored', ''))
        if 'Blockchain/Distributed Ledger Technology' in tech_explored:
            capability_score = min(capability_score + 1, 10)
            capability_components.append("blockchain_explored")
        if 'Biometric systems/Digital identity solutions' in tech_explored:
            capability_score = min(capability_score + 0.5, 10)
            capability_components.append("biometric_explored")

        capability_score = round(capability_score, 2)

        # ----- WILLINGNESS SCORE (0-5) -----
        willingness_score = 0
        willingness_components = []

        # Follow-up interview willingness
        followup = row.get('followup_willing')
        if followup == 'Yes':
            willingness_score += 3
            willingness_components.append("followup_yes")
        elif followup == 'Contact me with more information':
            willingness_score += 2
            willingness_components.append("followup_maybe")

        # Technology exploration history
        if tech_explored and len([t for t in tech_explored if t not in ['None of the above', '']]) > 0:
            willingness_score += 1
            willingness_components.append(f"tech_explored:{len(tech_explored)}")

        # Worker interest in credentials shows organizational openness
        if pd.notna(interest) and interest >= 3:
            willingness_score += 1
            willingness_components.append("worker_interest")

        willingness_score = min(willingness_score, 5)

        # ----- SCALE CONTEXT -----
        scale = {
            'temp_workers_count': row.get('temp_workers_count'),
            'elections_annually': row.get('elections_annually'),
        }

        # ----- COMPOSITE SCORE -----
        # Weighted composite: Need(40%) + Capability(35%) + Willingness(25%)
        # Normalize willingness from 0-5 to 0-10 for fair weighting
        composite = (need_score * 0.4) + (capability_score * 0.35) + ((willingness_score / 5) * 10 * 0.25)
        composite = round(composite, 2)

        # ----- PILOT SUITABILITY ASSESSMENT -----
        # Ideal: High need + adequate capability + expressed willingness
        if need_score >= 5 and capability_score >= 5 and willingness_score >= 3:
            suitability = 'HIGH'
        elif need_score >= 3 and capability_score >= 4 and willingness_score >= 2:
            suitability = 'MEDIUM'
        elif capability_score < 3:
            suitability = 'LOW - Infrastructure'
        elif need_score < 2:
            suitability = 'LOW - Limited Need'
        else:
            suitability = 'LOW'

        candidates.append({
            'country': country,
            'region': row.get('region'),
            'composite_score': composite,
            'need_score': need_score,
            'capability_score': capability_score,
            'willingness_score': willingness_score,
            'suitability': suitability,
            'need_components': need_components,
            'capability_components': capability_components,
            'willingness_components': willingness_components,
            'scale': scale,
        })

    # Sort by composite score
    candidates = sorted(candidates, key=lambda x: x['composite_score'], reverse=True)

    # Categorize candidates
    high_potential = [c for c in candidates if c['suitability'] == 'HIGH']
    medium_potential = [c for c in candidates if c['suitability'] == 'MEDIUM']
    low_potential = [c for c in candidates if c['suitability'].startswith('LOW')]

    return {
        'all_candidates': candidates,
        'high_potential': high_potential,
        'medium_potential': medium_potential,
        'low_potential': low_potential,
        'summary': {
            'total_assessed': len(candidates),
            'high_potential_count': len(high_potential),
            'medium_potential_count': len(medium_potential),
            'low_potential_count': len(low_potential),
            'top_5_candidates': [
                {
                    'country': c['country'],
                    'region': c['region'],
                    'composite_score': c['composite_score'],
                    'suitability': c['suitability'],
                }
                for c in candidates[:5]
            ],
        },
        'scoring_methodology': {
            'need_score': 'Pain points in blockchain-addressable areas (credential verification, training records, worker tracking). Scale 0-10.',
            'capability_score': 'Infrastructure readiness based on tech levels and limitations. Scale 0-10.',
            'willingness_score': 'Interest indicators (follow-up, tech exploration, worker interest). Scale 0-5.',
            'composite_formula': '(Need * 0.4) + (Capability * 0.35) + (Willingness_normalized * 0.25)',
            'suitability_criteria': {
                'HIGH': 'Need >= 5, Capability >= 5, Willingness >= 3',
                'MEDIUM': 'Need >= 3, Capability >= 4, Willingness >= 2',
                'LOW': 'Does not meet MEDIUM criteria or has blocking infrastructure issues',
            },
        },
    }


# =============================================================================
# Main Analysis Pipeline
# =============================================================================

def main():
    """Main segment analysis pipeline."""
    print("Loading cleaned survey data...")
    df = load_data()
    print(f"Loaded {len(df)} responses")

    # ==========================================================================
    # Regional Comparison
    # ==========================================================================
    print("\nCalculating regional comparisons...")
    regional_comparison = calculate_regional_comparison(df)

    regional_path = OUTPUT_DIR / "regional_comparison.json"
    with open(regional_path, 'w', encoding='utf-8') as f:
        json.dump(clean_for_json(regional_comparison), f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {regional_path}")

    # ==========================================================================
    # Infrastructure Segmentation
    # ==========================================================================
    print("\nSegmenting by infrastructure maturity...")
    infrastructure_segments = segment_by_infrastructure(df)

    infra_path = OUTPUT_DIR / "infrastructure_segments.json"
    with open(infra_path, 'w', encoding='utf-8') as f:
        json.dump(clean_for_json(infrastructure_segments), f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {infra_path}")

    # ==========================================================================
    # Pain Point Scoring
    # ==========================================================================
    print("\nCalculating pain point severity scores...")
    pain_points = calculate_pain_point_scores(df)

    pain_path = OUTPUT_DIR / "pain_point_rankings.json"
    with open(pain_path, 'w', encoding='utf-8') as f:
        json.dump(clean_for_json(pain_points), f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {pain_path}")

    # ==========================================================================
    # Pilot Candidate Scoring
    # ==========================================================================
    print("\nScoring pilot candidates...")
    pilot_candidates = calculate_pilot_scores(df)

    pilot_path = OUTPUT_DIR / "pilot_candidates.json"
    with open(pilot_path, 'w', encoding='utf-8') as f:
        json.dump(clean_for_json(pilot_candidates), f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {pilot_path}")

    # ==========================================================================
    # Print Summary
    # ==========================================================================
    print("\n" + "="*60)
    print("SEGMENT ANALYSIS SUMMARY")
    print("="*60)

    print("\n1. REGIONAL COMPARISON")
    for region, data in regional_comparison.items():
        print(f"   {region}:")
        print(f"     - Responses: {data['response_count']}")
        print(f"     - Countries: {', '.join(data['countries'][:3])}{'...' if len(data['countries']) > 3 else ''}")
        if data['training_confidence_mean']:
            print(f"     - Avg Training Confidence: {data['training_confidence_mean']}")

    print("\n2. INFRASTRUCTURE SEGMENTS")
    for segment, data in infrastructure_segments['segments'].items():
        print(f"   {segment.upper()}: {data['count']} respondents")
        if data['countries']:
            print(f"     Countries: {', '.join(data['countries'][:3])}{'...' if len(data['countries']) > 3 else ''}")

    print("\n3. PAIN POINT SEVERITY RANKING")
    for item in pain_points['area_ranking']:
        print(f"   {item['area']}: {item['avg_severity']:.1f} avg severity")

    print("\n4. PILOT CANDIDATES")
    summary = pilot_candidates['summary']
    print(f"   Total assessed: {summary['total_assessed']}")
    print(f"   HIGH potential: {summary['high_potential_count']}")
    print(f"   MEDIUM potential: {summary['medium_potential_count']}")
    print(f"   LOW potential: {summary['low_potential_count']}")

    print("\n   TOP 5 PILOT CANDIDATES:")
    for i, candidate in enumerate(summary['top_5_candidates'], 1):
        print(f"   {i}. {candidate['country']} ({candidate['region']})")
        print(f"      Score: {candidate['composite_score']} | Suitability: {candidate['suitability']}")

    print("\n" + "="*60)
    print(f"All outputs saved to: {OUTPUT_DIR}")
    print("="*60)

    return {
        'regional_comparison': regional_comparison,
        'infrastructure_segments': infrastructure_segments,
        'pain_points': pain_points,
        'pilot_candidates': pilot_candidates,
    }


if __name__ == "__main__":
    results = main()
