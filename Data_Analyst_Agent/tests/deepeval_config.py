# tests/deepeval_config.py
import os
from deepeval.models.base_model import DeepEvalBaseLLM
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OllamaEvaluator(DeepEvalBaseLLM):
    """
    DeepEval judge using local Ollama on NVIDIA RTX 5070 Ti.
    Model: qwen2.5:14b — strong evaluation quality.
    Completely free — no rate limits — runs on your GPU.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
        self.model_name = "qwen2.5:14b"

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.1,
            seed=None,           # ← disable seed
            extra_body={
                "cache": False,  # ← disable Ollama cache
                "keep_alive": 0  # ← don't keep model loaded between calls
            }
        )
        return response.choices[0].message.content
    
    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return self.model_name


evaluator = OllamaEvaluator()