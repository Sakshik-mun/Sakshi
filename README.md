# Credit Assistant

AI-driven credit health platform for the Indian ecosystem (CIBIL 300-900). FastAPI + React + Gemini.

## Run the backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY and SECRET_KEY
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

## Run the frontend
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
Open http://localhost:5173

## Scenarios
| Scenario | Endpoint |
|---|---|
| 1. Onboarding | `POST /auth/register`, `POST /profile` |
| 2. AI advice | `POST /advice` (cached until profile changes, 5/min limit) |
| 3. Progress chart | `GET /history` |
| 4. Monitoring | `PUT /profile` returns score delta; pie chart refreshes |
