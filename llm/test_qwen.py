from inference import generate

prompt = """
Patient ID: 5
Total PPC Score: 48
Risk Level: High

Question:
How to reduce postoperative pulmonary complications for this patient?
"""

response = generate(prompt)

print("\n🧠 MODEL RESPONSE:\n")
print(response)
