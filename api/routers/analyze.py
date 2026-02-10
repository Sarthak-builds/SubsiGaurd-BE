"""
Analyze endpoint for fraud detection.
"""
from fastapi import APIRouter, HTTPException
import pandas as pd

from models.schemas import AnalyzeRequest, AnalysisResult
from services.data_storage import storage
from services.fraud_detection import analyze_fraud

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalysisResult)
async def analyze_data(request: AnalyzeRequest) -> AnalysisResult:
    """
    Analyze uploaded data for fraud detection.
    
    Args:
        request: AnalyzeRequest with file_id
        
    Returns:
        AnalysisResult with summary and flagged records
        
    Raises:
        HTTPException: If file_id not found or analysis fails
    """
    # Retrieve data
    df = storage.get_data(request.file_id)
    
    if df is None:
        raise HTTPException(status_code=404, detail=f"File ID '{request.file_id}' not found")
    
    try:
        # Run fraud detection
        results = analyze_fraud(df)
        
        # Add file_id to results
        results['file_id'] = request.file_id
        
        # Store results
        storage.save_results(request.file_id, results)
        
        # Return as AnalysisResult
        return AnalysisResult(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")
