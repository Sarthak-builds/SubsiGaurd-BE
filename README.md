# SubsiGuard Backend
SubsiGuard Backend Implementation Plan
Goal Description
Build a complete FastAPI backend for SubsiGuard that handles CSV upload, temporary data storage, synthetic Indian subsidy data generation, rule-based + ML fraud detection, and result serving for the Next.js frontend. This is a hackathon MVP focused on demonstrating fraud detection capabilities without requiring external databases or cloud services.

User Review Required
IMPORTANT

Data Storage Strategy: Using in-memory dictionary storage for simplicity and speed. Data will be lost on server restart. For production, this should be replaced with persistent storage (SQLite, PostgreSQL, etc.).

IMPORTANT

ML Model: Using Isolation Forest (unsupervised anomaly detection) with contamination=0.08. No pre-training required, model fits on uploaded data. This is suitable for MVP but may need tuning based on actual fraud patterns.

IMPORTANT

Indian Data Localization: Synthetic data will include Indian states (MP, UP, Bihar, etc.), Aadhaar-like IDs, and INR amounts. Faker library will be used with custom logic for India-specific data.

Proposed Changes
Core Models & Schemas
[NEW] 
schemas.py
Define Pydantic models for:

UploadResponse: Contains file_id and preview (first 10 rows)
AnalyzeRequest: Contains file_id to analyze
FraudRecord: Individual record with fraud score, flag, and reasons
AnalysisResult: Summary statistics + flagged records list
SyntheticDataResponse: Generated synthetic data
Core Services
[NEW] 
data_storage.py
In-memory storage service using Python dict:

save_upload(file_id: str, df: pd.DataFrame): Store uploaded CSV
get_data(file_id: str) -> pd.DataFrame: Retrieve data by ID
save_results(file_id: str, results: dict): Store analysis results
get_results(file_id: str) -> dict: Retrieve results by ID
Thread-safe using locks for concurrent access
[NEW] 
synthetic_data.py
Generate realistic Indian subsidy data:

Use Faker library for names, dates, amounts
Custom logic for Aadhaar-like IDs (12 digits)
Indian states list (MP, UP, Bihar, Rajasthan, etc.)
Subsidy types (PM-KISAN, MGNREGA, LPG, etc.)
Inject 5-10% controlled fraud patterns:
Duplicate Aadhaar numbers
High income + high subsidy claims
Multiple claims same day from same distributor
Claims exceeding 3× average for state/subsidy type
[NEW] 
fraud_detection.py
Two-layer fraud detection:

Rule-Based Detection:

Duplicate beneficiary_id or aadhaar
Income > ₹250,000 threshold
Multiple claims (>2) on same date per distributor
Claim amount > 3× state/subsidy average
ML-Based Detection:

Isolation Forest from scikit-learn
Features: income, amount, claim frequency, distributor patterns
Contamination parameter: 0.08 (8% expected anomalies)
Returns anomaly score (normalized 0-1)
Output:

Per-record: fraud_score, is_fraud, reasons (list of triggered rules)
Summary: total_records, flagged_count, leakage_percent, high_risk_states
API Endpoints
[MODIFY] 
main.py
Include all routers and update CORS to only allow http://localhost:3000 (remove wildcard).

[NEW] 
upload.py
POST /upload

Accept CSV file via UploadFile
Parse with pandas
Validate required columns (beneficiary_id, aadhaar, income, amount, etc.)
Generate UUID as file_id
Store in data_storage
Return first 10 rows as preview + file_id
[NEW] 
analyze.py
POST /analyze

Accept file_id in request body
Retrieve data from storage
Run fraud detection (rules + ML)
Calculate summary statistics
Store results
Return AnalysisResult
[NEW] 
results.py
GET /results/{file_id}

Retrieve stored analysis results
Return 404 if not found
Return full AnalysisResult
[NEW] 
synthetic.py
GET /synthetic

Query param: rows (default 5000, max 10000)
Generate synthetic data with fraud injection
Return as JSON list of records
Verification Plan
Automated Tests
Since this is a hackathon MVP, we'll use manual testing with FastAPI's interactive docs:

Start server: uvicorn main:app --reload --port 8000
Access docs: Navigate to http://localhost:8000/docs
Manual Verification
Test 1: Health Check
Endpoint: GET /health
Expected: {"status": "healthy"}
Test 2: Synthetic Data Generation
Endpoint: GET /synthetic?rows=1000
Expected: JSON array with 1000 records
Verify: Check for Indian states, Aadhaar format (12 digits), subsidy types
Test 3: Upload → Analyze → Results Flow
Generate synthetic data: GET /synthetic?rows=5000
Save response as CSV (copy from browser, save as test_data.csv)
Upload CSV: POST /upload with file
Expected: file_id and preview of 10 rows
Analyze data: POST /analyze with {"file_id": "<file_id>"}
Expected: Summary with flagged records, leakage percentage
Retrieve results: GET /results/{file_id}
Expected: Same results as step 4
Test 4: CORS Verification
Run frontend: Start Next.js app on http://localhost:3000
Make API call from frontend to /health
Expected: No CORS errors in browser console
Test 5: Fraud Detection Validation
Check flagged records from Test 3 step 4
Verify reasons include rule-based flags (duplicate Aadhaar, high income, etc.)
Verify fraud_score is between 0 and 1
Check leakage_percent is reasonable (5-15% for synthetic data)
**Subsidy Leakage & Fraud Detection Dashboard** - FastAPI Backend

A production-ready FastAPI backend for detecting subsidy leakage and fraud patterns. Built for hackathon MVP with scalability in mind.

## Features

- ✅ FastAPI with automatic OpenAPI documentation
- ✅ CORS enabled for frontend integration
- ✅ Type hints throughout for better code quality
- ✅ Health check endpoint
- ✅ Ready for ML/fraud detection integration

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **SQLModel** - SQL database ORM
- **Pandas** - Data manipulation
- **Scikit-learn** - Machine learning
- **Faker** - Test data generation

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### API Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check endpoint

## Development

### Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Next Steps

- [ ] Add `fraud_detection.py` for ML models
- [ ] Add `database.py` for database connections
- [ ] Implement authentication
- [ ] Add data models with SQLModel
- [ ] Create fraud detection endpoints

## Environment Variables

Create a `.env` file for configuration:

```env
DATABASE_URL=sqlite:///./subsiguard.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## License

MIT License - Hackathon Project
