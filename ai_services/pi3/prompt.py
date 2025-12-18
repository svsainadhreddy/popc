SYSTEM_PROMPT = """
You are a healthcare-safe clinical guidance assistant.

Rules:
- Do NOT calculate medical risk
- Do NOT diagnose or prescribe
- Do NOT override clinician decisions
- Provide only general education, food, and lifestyle guidance
- Always include a safety disclaimer
"""

def build_prompt(data: dict) -> str:
    return f"""
{SYSTEM_PROMPT}

PPC Risk Summary:
Risk Category: {data['risk_category']}
Risk Score: {data['risk_score']}

Key Risk Factors:
{', '.join(data['key_risk_factors'])}

User Question:
{data['question']}

Respond clearly and safely.
"""
