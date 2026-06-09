# Research Internship Agent

An AI-powered platform to help students discover professors, analyze research, and manage personalized email outreach.

## Documentation

- [User Manual](USER_MANUAL.md): Step-by-step guide for platform users.
- [Frontend Deployment](frontend/DEPLOYMENT.md): Technical guide for Vercel deployment.

## Project Structure

- `frontend/`: Next.js application (App Router, TypeScript, TailwindCSS)
- `backend/`: FastAPI application (Python, Clean Architecture)

## Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deployment

### Frontend (Vercel)

See [frontend/DEPLOYMENT.md](frontend/DEPLOYMENT.md) for detailed instructions.

### Backend

Instructions for backend deployment pending.
