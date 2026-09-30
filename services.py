import os, json, re
import google.generativeai as genai

def calc_metrics(income, total_emi, credit_limit, credit_used):
    dti = round(total_emi / income * 100, 1) if income else 0
    util = round(credit_used / credit_limit * 100, 1) if credit_limit else 0
    return dti, util

def score_band(score):  # CIBIL 300-900
    if score >= 750: return "Excellent"
    if score >= 700: return "Good"
    if score >= 650: return "Fair"
    return "Poor"

def bottlenecks(score, dti, util):
    out = []
    if util > 30: out.append(f"High credit utilization ({util}%) - aim below 30%")
    if dti > 40: out.append(f"High debt-to-income ratio ({dti}%) - aim below 40%")
    if score < 650: out.append("Credit score below 650 - check for missed payments")
    return out

def get_advice(p):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    prompt = f"""You are a credit advisor for India. Score: {p.credit_score} (CIBIL, 300-900, band {score_band(p.credit_score)}),
DTI: {p.dti}%, utilization: {p.utilization}%, monthly income: Rs {p.monthly_income}, monthly expenses: Rs {p.monthly_expenses}.
Return ONLY JSON: {{"analysis": str, "bottlenecks": [str], "steps": [exactly 5 strings]}}.
Tailor steps to Indian banking (CIBIL, UPI-linked EMIs, credit card billing cycles, loan prepayment, secured cards).
Do not guarantee score outcomes."""
    last = None
    for _ in range(2):  # one retry
        try:
            text = model.generate_content(prompt).text
            text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
            data = json.loads(text)
            data["steps"] = data["steps"][:5]
            return data
        except Exception as e:
            last = e
    raise RuntimeError(f"Gemini failed: {last}")
