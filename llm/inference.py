from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import threading

MODEL_PATH = "llm/qwen_model"

class QwenPPCModel:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("🔹 Loading Qwen PPC model (CPU)...")

                    tokenizer = AutoTokenizer.from_pretrained(
                        MODEL_PATH,
                        trust_remote_code=True
                    )

                    model = AutoModelForCausalLM.from_pretrained(
                        MODEL_PATH,
                        torch_dtype=torch.float32,
                        device_map={"": "cpu"},
                        low_cpu_mem_usage=True
                    )

                    model.eval()
                    cls._instance = (tokenizer, model)

        return cls._instance

    @staticmethod
    def generate(prompt, max_tokens=120):
        tokenizer, model = QwenPPCModel.get()

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.4,            # ⬅ important
                top_p=0.85,
                do_sample=True,
                repetition_penalty=1.2,     # ⬅ prevents echo
                pad_token_id=tokenizer.eos_token_id
            )

        # 🔑 remove prompt from output
        input_len = inputs["input_ids"].shape[1]
        generated = output[0][input_len:]

        return tokenizer.decode(
            generated,
            skip_special_tokens=True
        ).strip()


# Django import helper
def generate(prompt, max_tokens=120):
    return QwenPPCModel.generate(prompt, max_tokens)
