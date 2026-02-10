from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

<<<<<<< HEAD
from api.routers import upload, analyze, results, synthetic

=======
>>>>>>> 0d5a0573b9f9cb33220711f178fd70e6ba37b538
app = FastAPI(
    title="SubsiGuard API",
    description="Subsidy Leakage & Fraud Detection Dashboard - Backend API",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["http://localhost:3000"],  # Frontend only
=======
    allow_origins=["http://localhost:3000", "*"],
>>>>>>> 0d5a0573b9f9cb33220711f178fd70e6ba37b538
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# Include routers
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(results.router)
app.include_router(synthetic.router)

=======
>>>>>>> 0d5a0573b9f9cb33220711f178fd70e6ba37b538

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
