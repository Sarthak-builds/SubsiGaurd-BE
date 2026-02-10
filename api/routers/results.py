"""
Results endpoint for retrieving analysis results.
"""
from fastapi import APIRouter, HTTPException

from models.schemas import AnalysisResult
from services.data_storage import storage

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{file_id}", response_model=AnalysisResult)
async def get_results(file_id: str) -> AnalysisResult:
    """
    Retrieve analysis results by file ID.
    
    Args:
        file_id: Unique file identifier
        
    Returns:
        AnalysisResult with summary and flagged records
        
    Raises:
        HTTPException: If file_id not found
    """
    results = storage.get_results(file_id)
    
    if results is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Results for file ID '{file_id}' not found. Please analyze the data first."
        )
    
    return AnalysisResult(**results)
