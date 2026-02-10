"""
Synthetic data generation endpoint.
"""
from fastapi import APIRouter, Query, HTTPException

from models.schemas import SyntheticDataResponse
from services.synthetic_data import generate_synthetic_data

router = APIRouter(prefix="/synthetic", tags=["synthetic"])


@router.get("", response_model=SyntheticDataResponse)
async def generate_synthetic(
    rows: int = Query(default=5000, ge=100, le=10000, description="Number of records to generate")
) -> SyntheticDataResponse:
    """
    Generate synthetic Indian subsidy data with fraud injection.
    
    Args:
        rows: Number of records to generate (100-10000, default 5000)
        
    Returns:
        SyntheticDataResponse with generated records
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        data = generate_synthetic_data(num_records=rows)
        return SyntheticDataResponse(**data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating synthetic data: {str(e)}")
