from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

app = FastAPI(
    title="SubsiGuard API",
    description="Subsidy Leakage & Fraud Detection Dashboard - Backend API",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        Dict[str, str]: Status message indicating the API health.
    """
    return {"status": "healthy"}


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """
    Root endpoint with API information.
    
    Returns:
        Dict[str, str]: Welcome message and API details.
    """
    return {
        "message": "SubsiGuard API",
        "version": "1.0.0",
        "docs": "/docs"
    }
