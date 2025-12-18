from fastapi import FastAPI
from model_loader import Phi3LLM
from prompt import build_prompt
from schemas import Phi3Request, Phi3Response

app = FastAPI(title="Phi-3 PPC Guidance Service")

llm = Phi3LLM()

@app.post("/ppc-guidance", response_model=Phi3Response)
def generate_guidance(data: Phi3Request):
    prompt = build_prompt(data.dict())
    output = llm.generate(prompt)
    return Phi3Response(response=output)
