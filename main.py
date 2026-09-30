import os, json
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from . import models, schemas, services
from .auth import hash_password, verify_password, create_token, current_user
from .database import Base, engine, get_db

Base.metadata.create_all(engine)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Credit Assistant")
app.state.limiter = limiter
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
                   allow_methods=["*"], allow_headers=["*"])

@app.post("/auth/register", status_code=201)
def register(body: schemas.RegisterIn, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=body.email).first():
        raise HTTPException(400, "Email already registered")
    u = models.User(name=body.name, email=body.email, hashed_password=hash_password(body.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"access_token": create_token(u.id), "token_type": "bearer"}

@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    u = db.query(models.User).filter_by(email=form.username).first()
    if not u or not verify_password(form.password, u.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_token(u.id), "token_type": "bearer"}

def _apply(p, body, db, user):
    p.monthly_income, p.monthly_expenses = body.monthly_income, body.monthly_expenses
    p.total_emi, p.credit_limit = body.total_emi, body.credit_limit
    p.credit_used, p.credit_score = body.credit_used, body.credit_score
    p.dti, p.utilization = services.calc_metrics(p.monthly_income, p.total_emi, p.credit_limit, p.credit_used)
    p.updated_at, p.last_advice = datetime.utcnow(), None  # invalidate cached advice
    db.add(models.ScoreHistory(user_id=user.id, score=p.credit_score, dti=p.dti, utilization=p.utilization))

def _view(p, delta=0):
    return {
        "credit_score": p.credit_score, "band": services.score_band(p.credit_score),
        "dti": p.dti, "utilization": p.utilization, "delta": delta,
        "monthly_income": p.monthly_income, "monthly_expenses": p.monthly_expenses,
        "total_emi": p.total_emi, "credit_limit": p.credit_limit, "credit_used": p.credit_used,
        "available_credit": p.credit_limit - p.credit_used,
        "bottlenecks": services.bottlenecks(p.credit_score, p.dti, p.utilization),
    }

@app.get("/profile")
def get_profile(db: Session = Depends(get_db), user=Depends(current_user)):
    p = db.query(models.FinancialProfile).filter_by(user_id=user.id).first()
    if not p: raise HTTPException(404, "Profile not set up")
    return {**_view(p), "name": user.name}

@app.post("/profile", status_code=201)
def create_profile(body: schemas.ProfileIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if db.query(models.FinancialProfile).filter_by(user_id=user.id).first():
        raise HTTPException(400, "Profile exists; use PUT")
    p = models.FinancialProfile(user_id=user.id)
    _apply(p, body, db, user); db.add(p); db.commit(); db.refresh(p)
    return _view(p)

@app.put("/profile")
def update_profile(body: schemas.ProfileIn, db: Session = Depends(get_db), user=Depends(current_user)):
    p = db.query(models.FinancialProfile).filter_by(user_id=user.id).first()
    if not p: raise HTTPException(404, "Profile not set up")
    last = db.query(models.ScoreHistory).filter_by(user_id=user.id).order_by(models.ScoreHistory.id.desc()).first()
    _apply(p, body, db, user); db.commit()
    return _view(p, delta=p.credit_score - last.score if last else 0)

@app.get("/history")
def history(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(models.ScoreHistory).filter_by(user_id=user.id).order_by(models.ScoreHistory.recorded_at).all()
    return [{"score": r.score, "dti": r.dti, "utilization": r.utilization,
             "date": r.recorded_at.strftime("%d %b %Y")} for r in rows]

@app.post("/advice")
@limiter.limit("5/minute")
def advice(request: Request, db: Session = Depends(get_db), user=Depends(current_user)):
    p = db.query(models.FinancialProfile).filter_by(user_id=user.id).first()
    if not p: raise HTTPException(404, "Profile not set up")
    if p.last_advice: return json.loads(p.last_advice)
    try:
        data = services.get_advice(p)
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    p.last_advice = json.dumps(data); db.commit()
    return data
