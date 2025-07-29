import os
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

# 載入 .env.local（優先較低）
load_dotenv(".env.local", override=False)

# 載入 .env（優先較高，會覆蓋已存在的）
load_dotenv(".env", override=True)

class Settings(BaseSettings):
    """
    Settings for the application, loaded from environment variables or a .env file.
    """

    # AI Model Provider URLs
    openai_api_url: str
    openrouter_api_url: str
    ollama_api_url: str

    # AI Model Provider Keys
    openai_api_key: str
    openrouter_api_key: str
    genai_api_key: str
    hf_token: str

    # LLM settings
    provider: str
    model_name: str
    temperature: float
    top_p: float
    max_tokens: int

    class Config:
        # env_file 保留，但實際上上面已經用 dotenv 載入環境變數
        env_file = None

# 初始化設定
setting = Settings()
