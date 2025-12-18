from pydantic import BaseModel
from typing import List

class Phi3Request(BaseModel):
    risk_category: str
    risk_score: int
    key_risk_factors: List[str]
    question: str

class Phi3Response(BaseModel):
    response: str
