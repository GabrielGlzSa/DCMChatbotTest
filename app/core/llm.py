from langchain.chat_models import ChatOpenAI
from functools import lru_cache
import os

VLLM_SERVER = os.getenv("VLLM_SERVER", "http://vllm:8000/v1")
    
@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=VLLM_SERVER,
        api_key="not-needed",
        model_name="meta-llama/Llama-3.2-3B-Instruct",
        temperature=0.2,
        max_tokens=512
    )
