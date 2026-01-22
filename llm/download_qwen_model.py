from transformers import AutoTokenizer, AutoModelForCausalLM
import os

MODEL_NAME = "Qwen/Qwen2-0.5B-Instruct"
SAVE_PATH = "llm/qwen_model"

os.makedirs(SAVE_PATH, exist_ok=True)

print("Downloading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

print("Downloading model (this may take a few minutes)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("Saving model locally...")
tokenizer.save_pretrained(SAVE_PATH)
model.save_pretrained(SAVE_PATH)

print("✅ Model downloaded and saved to:", SAVE_PATH)
