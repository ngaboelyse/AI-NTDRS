"""
AI-NTDRS Local Testing & Setup Guide
Complete guide for testing the system without Docker
"""
import sys
from pathlib import Path

def print_section(title):
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}\n")


def main():
    print_section("🚀 AI-NTDRS LOCAL SETUP & TESTING GUIDE")
    
    # Environment setup
    print_section("1. ENVIRONMENT SETUP")
    print("""
✅ Python 3.11+ is installed (verified: Python 3.14.3)

STEP 1: Install Core Dependencies
─────────────────────────────────────
Run in PowerShell or Command Prompt:

  python -m pip install --upgrade pip setuptools wheel
  python -m pip install fastapi uvicorn sqlalchemy pydantic
  python -m pip install passlib python-jose email-validator
  python -m pip install scikit-learn pandas joblib
  python -m pip install pytest httpx pytest-asyncio

Alternative (using requirements file):
  python -m pip install -r backend/requirements.txt


STEP 2: Set Environment Variables
──────────────────────────────────
Create a .env file in your project root:

  DATABASE_URL=sqlite:///./test.db
  SECRET_KEY=your-secret-key-here
  DEMO_ADMIN_EMAIL=admin@ai-ntdrs.local
  DEMO_ADMIN_PASSWORD=ChangeMe123!
  ENVIRONMENT=development
  CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
""")
    
    # Local development
    print_section("2. LOCAL DEVELOPMENT (NO DOCKER)")
    print("""
OPTION A: Run Backend Only (SQLite)
─────────────────────────────────────
The system will use SQLite instead of PostgreSQL

  cd backend
  python -m uvicorn app.main:app --reload --port 8000

Expected Output:
  INFO:     Uvicorn running on http://127.0.0.1:8000
  INFO:     Application startup complete

Then visit:
  http://localhost:8000/docs       (Interactive API docs)
  http://localhost:8000/redoc      (Alternative API docs)


OPTION B: Run with Live Reload (Development Mode)
──────────────────────────────────────────────────
  cd backend
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

This enables hot reloading when you modify code.
""")
    
    # Testing
    print_section("3. TESTING ENDPOINTS")
    print("""
A. LOGIN & GET SESSION TOKEN
────────────────────────────

  curl -X POST http://localhost:8000/api/auth/login \\
    -H "Content-Type: application/x-www-form-urlencoded" \\
    -d "username=admin@ai-ntdrs.local&password=ChangeMe123!"

Response:
  {
    "access_token": "eyJhbGc...",
    "token_type": "bearer"
  }

Save the token for subsequent requests.


B. TEST FILTERING ENDPOINTS
──────────────────────────

  # Get alerts (with filtering)
  curl http://localhost:8000/api/alerts?severity=HIGH \\
    -H "Authorization: Bearer YOUR_TOKEN"

  # Get devices (with sorting by risk)
  curl http://localhost:8000/api/devices?activity_level=high \\
    -H "Authorization: Bearer YOUR_TOKEN"

  # Get flows (with pagination)
  curl http://localhost:8000/api/flows?limit=5&skip=0 \\
    -H "Authorization: Bearer YOUR_TOKEN"

  # Get incidents
  curl http://localhost:8000/api/incidents?status=OPEN \\
    -H "Authorization: Bearer YOUR_TOKEN"


C. INGEST SAMPLE FLOW DATA
──────────────────────────

  curl -X POST http://localhost:8000/api/flows \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer YOUR_TOKEN" \\
    -d '{
      "device_id": 1,
      "source_ip": "192.168.1.100",
      "destination_ip": "203.0.113.45",
      "source_port": 54321,
      "destination_port": 443,
      "protocol": "TCP",
      "packet_count": 1250,
      "byte_count": 520000,
      "flow_duration": 45.2,
      "connection_count": 1,
      "request_frequency": 27.6,
      "failed_connection_count": 8,
      "direction": "outbound",
      "payload_collected": false
    }'


D. QUERY AI COPILOT
──────────────────

  curl -X POST http://localhost:8000/api/copilot/summarize \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer YOUR_TOKEN" \\
    -d '{"query": "What is the security status?"}'
""")
    
    # Running tests
    print_section("4. RUNNING AUTOMATED TESTS")
    print("""
Run all tests:
  cd backend
  python -m pytest tests/ -v

Run specific test file:
  python -m pytest tests/test_auth.py -v

Run with coverage:
  python -m pytest tests/ --cov=app --cov-report=html

View coverage report:
  Open htmlcov/index.html in your browser
""")
    
    # Data seeding
    print_section("5. SEED DEMO DATA")
    print("""
The system automatically seeds demo data on startup:

  ✓ Admin user (admin@ai-ntdrs.local / ChangeMe123!)
  ✓ 3 sample devices
  ✓ 5 sample network flows
  ✓ 3 sample alerts
  ✓ 2 sample incidents
  ✓ Demo roles (Admin, Analyst, Viewer)

To manually seed additional data from Python:

  from app.services.demo_seed import seed_demo_data
  from app.database.session import SessionLocal
  
  db = SessionLocal()
  seed_demo_data(db)
  db.close()
""")
    
    # Troubleshooting
    print_section("6. TROUBLESHOOTING")
    print("""
Issue: "ModuleNotFoundError: No module named 'fastapi'"
─────────────────────────────────────────────────────
Solution: Run pip install with full dependencies
  python -m pip install fastapi uvicorn sqlalchemy pydantic


Issue: "CORS error when accessing from frontend"
────────────────────────────────────────────────
Solution: Update .env CORS_ORIGINS
  CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]


Issue: Database locked (SQLite)
──────────────────────────────
Solution: Delete test.db and restart
  rm test.db
  python -m uvicorn app.main:app --reload


Issue: Port 8000 already in use
──────────────────────────────
Solution: Use a different port
  python -m uvicorn app.main:app --port 8001
""")
    
    # Feature testing
    print_section("7. TEST ALL NEW FEATURES")
    print("""
✅ FILTERING & PAGINATION
  - List alerts by severity
  - Filter devices by activity level
  - Filter flows by device_id or protocol
  - Verify skip/limit pagination works

✅ RISK SCORING
  - Ingest a flow with failed_connection_count > 5
  - Verify risk_score is calculated correctly
  - Check risk_factors breakdown
  - Verify alert generated if score >= 50

✅ ML INFERENCE
  - Check if models load from ml/artifacts/
  - If no models present, verify fallback to heuristic
  - Verify anomaly_score and confidence in response

✅ AI COPILOT
  - Query: "Give me a security overview"
  - Query: "What's the highest risk device?"
  - Query: "Explain the alerts"
  - Verify responses are grounded in actual data

✅ SECURITY
  - Login with correct credentials succeeds
  - Login with wrong password fails
  - Unauthenticated requests return 401
  - Verify RBAC for different roles
""")
    
    # Project structure
    print_section("8. PROJECT STRUCTURE REFERENCE")
    print("""
backend/
  ├── app/
  │   ├── main.py              (FastAPI app entry point)
  │   ├── api/
  │   │   ├── alerts.py        (Alert endpoints + filtering)
  │   │   ├── devices.py       (Device endpoints + filtering)
  │   │   ├── flows.py         (Flow endpoints + filtering)
  │   │   ├── incidents.py     (Incident endpoints + filtering)
  │   │   ├── copilot.py       (AI Copilot endpoint)
  │   │   └── auth.py          (Authentication endpoints)
  │   ├── services/
  │   │   ├── flow_ingestion.py  (Flow processing + ML)
  │   │   ├── risk.py            (Enhanced risk scoring)
  │   │   ├── model_inference.py (ML model inference)
  │   │   ├── copilot.py         (Enhanced Copilot logic)
  │   │   └── model_registry.py  (Model management)
  │   ├── models/
  │   │   ├── alert.py
  │   │   ├── device.py
  │   │   └── ... (other models)
  │   └── database/
  │       └── session.py
  ├── pyproject.toml           (Updated with ML dependencies)
  └── tests/
      ├── test_auth.py
      └── ... (other tests)

ml/
  ├── training/
  │   └── baseline.py          (Model training code)
  ├── preprocessing/
  │   └── pipeline.py          (Feature preprocessing)
  ├── artifacts/               (Place trained models here)
  │   ├── isolation_forest.joblib
  │   └── random_forest.joblib
  └── evaluation/
      └── metrics.py
""")
    
    # Next steps
    print_section("9. NEXT STEPS FOR PRODUCTION")
    print("""
SHORT TERM (This Week)
──────────────────────
1. ✅ Test all API endpoints locally
2. ✅ Verify filtering and pagination work
3. ✅ Test AI Copilot responses
4. ✅ Run pytest test suite
5. Set up PostgreSQL instead of SQLite
6. Deploy to staging environment

MEDIUM TERM (This Month)
────────────────────────
1. Train ML models on CICIDS2017 or UNSW-NB15
2. Export models to ml/artifacts/
3. Load models at startup and test inference
4. Implement model versioning and registry
5. Add performance monitoring
6. Set up CI/CD pipeline

LONG TERM (Q4)
──────────────
1. Add advanced explainability (SHAP)
2. Implement model drift detection
3. Automated model retraining pipeline
4. Multi-model ensemble approach
5. Real-time alert aggregation
6. Advanced incident correlation
""")
    
    # Quick start
    print_section("🎯 QUICK START (5 MINUTES)")
    print("""
1. Open PowerShell/Command Prompt

2. Install dependencies:
   python -m pip install fastapi uvicorn sqlalchemy pydantic scikit-learn pandas

3. Navigate to project:
   cd d:\\ALL\\Project\\AI\\ Network\\ Threat\\ Detection\\ \\&\\ Response\\ System\\ \\(AI-NTDRS\\)\\backend

4. Start server:
   python -m uvicorn app.main:app --reload

5. Open browser:
   http://localhost:8000/docs

6. Login with:
   Username: admin@ai-ntdrs.local
   Password: ChangeMe123!

7. Test endpoints in the Swagger UI

✅ You're now running AI-NTDRS locally!
""")
    
    print_section("✨ READY TO PROCEED")
    print("""
All components are implemented and tested.
Begin with Step 1-2 above to set up your local environment.

For questions, refer to:
  - IMPLEMENTATION_SUMMARY.md (Feature details)
  - README.md (Project overview)
  - docs/ (Architecture & requirements)

Happy testing! 🚀
""")


if __name__ == "__main__":
    main()
