import requests

PHI3_URL = "http://127.0.0.1:9000/ppc-guidance"

def get_phi3_guidance(risk_category, risk_score, factors, question):
    payload = {
        "risk_category": risk_category,
        "risk_score": risk_score,
        "key_risk_factors": factors,
        "question": question
    }

    response = requests.post(PHI3_URL, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["response"]
