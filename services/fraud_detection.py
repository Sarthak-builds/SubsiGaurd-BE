"""
Fraud detection engine with rule-based and ML-based detection.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from collections import Counter


def detect_duplicate_beneficiaries(df: pd.DataFrame) -> pd.Series:
    """Detect duplicate beneficiary IDs."""
    return df.duplicated(subset=['beneficiary_id'], keep=False)


def detect_duplicate_aadhaar(df: pd.DataFrame) -> pd.Series:
    """Detect duplicate Aadhaar numbers."""
    return df.duplicated(subset=['aadhaar'], keep=False)


def detect_high_income(df: pd.DataFrame, threshold: float = 250000) -> pd.Series:
    """Detect beneficiaries with income above threshold."""
    return df['income'] > threshold


def detect_multiple_claims_same_day(df: pd.DataFrame) -> pd.Series:
    """Detect multiple claims on same date from same distributor."""
    claim_counts = df.groupby(['distributor_id', 'claim_date']).size()
    suspicious = claim_counts[claim_counts > 2].index
    return df.set_index(['distributor_id', 'claim_date']).index.isin(suspicious)


def detect_excessive_amounts(df: pd.DataFrame, multiplier: float = 3.0) -> pd.Series:
    """Detect claims exceeding 3x average for state/subsidy type."""
    avg_amounts = df.groupby(['location_state', 'subsidy_type'])['amount'].transform('mean')
    return df['amount'] > (avg_amounts * multiplier)


def apply_rule_based_detection(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply rule-based fraud detection.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with additional columns for each rule
    """
    df = df.copy()
    
    df['rule_duplicate_beneficiary'] = detect_duplicate_beneficiaries(df)
    df['rule_duplicate_aadhaar'] = detect_duplicate_aadhaar(df)
    df['rule_high_income'] = detect_high_income(df)
    df['rule_multiple_claims'] = detect_multiple_claims_same_day(df)
    df['rule_excessive_amount'] = detect_excessive_amounts(df)
    
    # Count triggered rules
    rule_columns = [col for col in df.columns if col.startswith('rule_')]
    df['rules_triggered_count'] = df[rule_columns].sum(axis=1)
    
    return df


def prepare_features_for_ml(df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
    """
    Prepare features for ML model.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (feature array, feature names)
    """
    df_ml = df.copy()
    
    # Encode categorical variables
    le_state = LabelEncoder()
    le_subsidy = LabelEncoder()
    le_distributor = LabelEncoder()
    
    df_ml['state_encoded'] = le_state.fit_transform(df_ml['location_state'])
    df_ml['subsidy_encoded'] = le_subsidy.fit_transform(df_ml['subsidy_type'])
    df_ml['distributor_encoded'] = le_distributor.fit_transform(df_ml['distributor_id'])
    
    # Calculate claim frequency per beneficiary
    claim_freq = df_ml.groupby('beneficiary_id').size()
    df_ml['claim_frequency'] = df_ml['beneficiary_id'].map(claim_freq)
    
    # Feature selection
    feature_columns = [
        'income',
        'amount',
        'state_encoded',
        'subsidy_encoded',
        'distributor_encoded',
        'claim_frequency'
    ]
    
    features = df_ml[feature_columns].values
    
    return features, feature_columns


def apply_ml_detection(df: pd.DataFrame, contamination: float = 0.08) -> np.ndarray:
    """
    Apply Isolation Forest for anomaly detection.
    
    Args:
        df: Input DataFrame
        contamination: Expected proportion of outliers (default 8%)
        
    Returns:
        Array of anomaly scores (normalized 0-1, higher = more anomalous)
    """
    features, _ = prepare_features_for_ml(df)
    
    # Train Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100
    )
    
    # Fit and predict (-1 for anomalies, 1 for normal)
    predictions = iso_forest.fit_predict(features)
    
    # Get anomaly scores (lower = more anomalous)
    scores = iso_forest.score_samples(features)
    
    # Normalize scores to 0-1 range (higher = more anomalous)
    normalized_scores = 1 - ((scores - scores.min()) / (scores.max() - scores.min()))
    
    return normalized_scores


def generate_fraud_reasons(row: pd.Series) -> List[str]:
    """Generate human-readable fraud reasons for a record."""
    reasons = []
    
    if row.get('rule_duplicate_beneficiary', False):
        reasons.append("Duplicate beneficiary ID detected")
    
    if row.get('rule_duplicate_aadhaar', False):
        reasons.append("Duplicate Aadhaar number detected")
    
    if row.get('rule_high_income', False):
        reasons.append(f"High income (₹{row['income']:,.0f}) for subsidy recipient")
    
    if row.get('rule_multiple_claims', False):
        reasons.append("Multiple claims on same date from same distributor")
    
    if row.get('rule_excessive_amount', False):
        reasons.append(f"Claim amount (₹{row['amount']:,.0f}) exceeds 3x average for state/subsidy type")
    
    if row.get('fraud_score', 0) > 0.7:
        reasons.append(f"High ML anomaly score ({row['fraud_score']:.2f})")
    
    return reasons


def analyze_fraud(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform complete fraud analysis on dataset.
    
    Args:
        df: Input DataFrame with subsidy records
        
    Returns:
        Dictionary with analysis results
    """
    # Apply rule-based detection
    df_analyzed = apply_rule_based_detection(df)
    
    # Apply ML-based detection
    ml_scores = apply_ml_detection(df)
    df_analyzed['ml_anomaly_score'] = ml_scores
    
    # Combine rule-based and ML scores
    # Weight: 60% rules, 40% ML
    rule_score = df_analyzed['rules_triggered_count'] / 5.0  # Normalize by max possible rules
    df_analyzed['fraud_score'] = (0.6 * rule_score + 0.4 * df_analyzed['ml_anomaly_score']).clip(0, 1)
    
    # Flag as fraud if score > 0.5 OR 2+ rules triggered
    df_analyzed['is_fraud'] = (df_analyzed['fraud_score'] > 0.5) | (df_analyzed['rules_triggered_count'] >= 2)
    
    # Generate reasons for each record
    df_analyzed['reasons'] = df_analyzed.apply(generate_fraud_reasons, axis=1)
    
    # Calculate summary statistics
    total_records = len(df_analyzed)
    flagged_count = df_analyzed['is_fraud'].sum()
    total_amount = df_analyzed['amount'].sum()
    flagged_amount = df_analyzed[df_analyzed['is_fraud']]['amount'].sum()
    leakage_percent = (flagged_amount / total_amount * 100) if total_amount > 0 else 0
    
    # Identify high-risk states
    state_fraud_counts = df_analyzed[df_analyzed['is_fraud']].groupby('location_state').size()
    high_risk_states = state_fraud_counts.nlargest(5).to_dict()
    
    # Get flagged records
    flagged_df = df_analyzed[df_analyzed['is_fraud']].copy()
    flagged_records = flagged_df.to_dict('records')
    
    # Summary
    summary = {
        "total_records": int(total_records),
        "flagged_count": int(flagged_count),
        "leakage_percent": round(float(leakage_percent), 2),
        "total_amount": round(float(total_amount), 2),
        "flagged_amount": round(float(flagged_amount), 2),
        "high_risk_states": {k: int(v) for k, v in high_risk_states.items()}
    }
    
    return {
        "summary": summary,
        "flagged_records": flagged_records,
        "total_records": int(total_records),
        "flagged_count": int(flagged_count),
        "leakage_percent": round(float(leakage_percent), 2)
    }
