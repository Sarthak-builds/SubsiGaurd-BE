"""
Pydantic schemas for SubsiGuard API request/response models.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response model for CSV upload endpoint."""
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    preview: List[Dict[str, Any]] = Field(..., description="First 10 rows of uploaded data")
    total_rows: int = Field(..., description="Total number of rows in the uploaded file")


class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint."""
    file_id: str = Field(..., description="File ID to analyze")


class FraudRecord(BaseModel):
    """Individual fraud record with detection details."""
    beneficiary_id: str
    name: str
    aadhaar: str
    income: float
    location_state: str
    subsidy_type: str
    amount: float
    claim_date: str
    distributor_id: str
    fraud_score: float = Field(..., ge=0.0, le=1.0, description="Fraud probability score (0-1)")
    is_fraud: bool = Field(..., description="Whether record is flagged as fraudulent")
    reasons: List[str] = Field(default_factory=list, description="List of fraud indicators")


class AnalysisResult(BaseModel):
    """Complete analysis result with summary and flagged records."""
    file_id: str
    summary: Dict[str, Any] = Field(
        ..., 
        description="Summary statistics including total_records, flagged_count, leakage_percent, high_risk_states"
    )
    flagged_records: List[FraudRecord] = Field(..., description="List of records flagged as fraudulent")
    total_records: int
    flagged_count: int
    leakage_percent: float


class SyntheticRecord(BaseModel):
    """Single synthetic subsidy record."""
    beneficiary_id: str
    name: str
    aadhaar: str
    income: float
    location_state: str
    subsidy_type: str
    amount: float
    claim_date: str
    distributor_id: str


class SyntheticDataResponse(BaseModel):
    """Response model for synthetic data generation."""
    records: List[SyntheticRecord]
    total_count: int
    fraud_injected_count: int = Field(..., description="Number of synthetic fraud cases injected")
