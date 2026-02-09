# SubsiGuard Backend

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
