"""
Upload endpoint for CSV file processing.
"""
import uuid
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from io import StringIO

from models.schemas import UploadResponse
from services.data_storage import storage

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload and parse CSV file containing subsidy data.
    
    Args:
        file: CSV file upload
        
    Returns:
        UploadResponse with file_id, preview, and total_rows
        
    Raises:
        HTTPException: If file is not CSV or parsing fails
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read file content
        content = await file.read()
        csv_string = content.decode('utf-8')
        
        # Parse CSV with pandas
        df = pd.read_csv(StringIO(csv_string))
        
        # Validate required columns
        required_columns = [
            'beneficiary_id', 'name', 'aadhaar', 'income', 
            'location_state', 'subsidy_type', 'amount', 
            'claim_date', 'distributor_id'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Store data
        storage.save_upload(file_id, df)
        
        # Get preview (first 10 rows)
        preview = df.head(10).to_dict('records')
        
        return UploadResponse(
            file_id=file_id,
            preview=preview,
            total_rows=len(df)
        )
        
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
