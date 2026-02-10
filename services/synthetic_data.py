"""
Synthetic Indian subsidy data generator with controlled fraud injection.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker

# Initialize Faker
fake = Faker('en_IN')  # Indian locale

# Indian states (focus on major subsidy-receiving states)
INDIAN_STATES = [
    "Madhya Pradesh", "Uttar Pradesh", "Bihar", "Rajasthan", "Maharashtra",
    "West Bengal", "Odisha", "Karnataka", "Gujarat", "Tamil Nadu",
    "Andhra Pradesh", "Telangana", "Punjab", "Haryana", "Jharkhand"
]

# Common subsidy schemes in India
SUBSIDY_TYPES = [
    "PM-KISAN",           # Direct cash to farmers
    "MGNREGA",            # Rural employment
    "LPG Subsidy",        # Cooking gas
    "Ration Card",        # Food subsidy
    "Scholarship",        # Education
    "Pension",            # Old age/widow pension
    "Housing Subsidy",    # PMAY
    "Fertilizer Subsidy"  # Agriculture
]

# Subsidy amount ranges (in INR)
SUBSIDY_RANGES = {
    "PM-KISAN": (2000, 6000),
    "MGNREGA": (3000, 15000),
    "LPG Subsidy": (200, 600),
    "Ration Card": (500, 2000),
    "Scholarship": (5000, 50000),
    "Pension": (1000, 3000),
    "Housing Subsidy": (50000, 250000),
    "Fertilizer Subsidy": (1000, 10000)
}


def generate_aadhaar() -> str:
    """Generate a fake 12-digit Aadhaar-like number."""
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])


def generate_beneficiary_id() -> str:
    """Generate a unique beneficiary ID."""
    prefix = random.choice(['BEN', 'SUB', 'REC'])
    number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefix}{number}"


def generate_distributor_id() -> str:
    """Generate a distributor/office ID."""
    prefix = random.choice(['DIST', 'OFF', 'CTR'])
    number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{prefix}{number}"


def generate_clean_record() -> Dict[str, Any]:
    """Generate a single clean (non-fraudulent) subsidy record."""
    subsidy_type = random.choice(SUBSIDY_TYPES)
    min_amt, max_amt = SUBSIDY_RANGES[subsidy_type]
    
    # Generate claim date within last 2 years
    days_ago = random.randint(0, 730)
    claim_date = datetime.now() - timedelta(days=days_ago)
    
    # Income distribution (most beneficiaries should be low income)
    income = random.choices(
        [random.randint(0, 100000), random.randint(100000, 250000), random.randint(250000, 500000)],
        weights=[70, 25, 5]  # 70% low income, 25% middle, 5% high
    )[0]
    
    return {
        "beneficiary_id": generate_beneficiary_id(),
        "name": fake.name(),
        "aadhaar": generate_aadhaar(),
        "income": float(income),
        "location_state": random.choice(INDIAN_STATES),
        "subsidy_type": subsidy_type,
        "amount": float(random.randint(min_amt, max_amt)),
        "claim_date": claim_date.strftime("%Y-%m-%d"),
        "distributor_id": generate_distributor_id()
    }


def inject_fraud_patterns(records: List[Dict[str, Any]], fraud_percentage: float = 0.08) -> List[Dict[str, Any]]:
    """
    Inject controlled fraud patterns into the dataset.
    
    Args:
        records: List of clean records
        fraud_percentage: Percentage of records to make fraudulent (default 8%)
        
    Returns:
        Records with fraud patterns injected
    """
    num_fraud = int(len(records) * fraud_percentage)
    fraud_indices = random.sample(range(len(records)), num_fraud)
    
    for idx in fraud_indices:
        fraud_type = random.choice(['duplicate_aadhaar', 'high_income', 'multiple_claims', 'excessive_amount'])
        
        if fraud_type == 'duplicate_aadhaar':
            # Use an existing Aadhaar from another record
            other_idx = random.choice([i for i in range(len(records)) if i != idx])
            records[idx]['aadhaar'] = records[other_idx]['aadhaar']
        
        elif fraud_type == 'high_income':
            # High income but claiming subsidy
            records[idx]['income'] = float(random.randint(300000, 1000000))
        
        elif fraud_type == 'multiple_claims':
            # Multiple claims on same date from same distributor
            other_idx = random.choice([i for i in range(len(records)) if i != idx])
            records[idx]['claim_date'] = records[other_idx]['claim_date']
            records[idx]['distributor_id'] = records[other_idx]['distributor_id']
        
        elif fraud_type == 'excessive_amount':
            # Amount 3-5x the normal range
            subsidy_type = records[idx]['subsidy_type']
            _, max_amt = SUBSIDY_RANGES[subsidy_type]
            records[idx]['amount'] = float(max_amt * random.uniform(3, 5))
    
    return records


def generate_synthetic_data(num_records: int = 5000, fraud_percentage: float = 0.08) -> Dict[str, Any]:
    """
    Generate synthetic Indian subsidy data with fraud injection.
    
    Args:
        num_records: Number of records to generate (default 5000)
        fraud_percentage: Percentage of fraudulent records (default 8%)
        
    Returns:
        Dictionary with records, total_count, and fraud_injected_count
    """
    # Generate clean records
    records = [generate_clean_record() for _ in range(num_records)]
    
    # Inject fraud patterns
    records = inject_fraud_patterns(records, fraud_percentage)
    
    fraud_count = int(num_records * fraud_percentage)
    
    return {
        "records": records,
        "total_count": num_records,
        "fraud_injected_count": fraud_count
    }
