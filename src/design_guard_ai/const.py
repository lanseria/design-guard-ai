"""Configuration module with .env support"""
import os
from pathlib import Path
from dotenv import load_dotenv

def reload_env():
    """重新加载.env文件"""
    BASE_DIR = Path(__file__).parent.parent
    load_dotenv(BASE_DIR / ".env", override=True)

# 初始加载 .env 文件
reload_env()

# AI 供应商配置（优先读取环境变量）
def get_ai_vendor():
    return os.getenv("AI_VENDOR", "google")  # 默认使用 Google

# API 密钥配置（优先读取环境变量）
def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY", "")

def get_dify_api_key():
    return os.getenv("DIFY_API_KEY", "")

def get_dify_dataset_id():
    return os.getenv("DIFY_DATASET_ID", "")

# 根据供应商选择默认模型
def get_llm_model():
    return os.getenv("LLM_MODEL")

def get_openrouter_api_key():
    return os.getenv("OPENROUTER_API_KEY", "")

def get_openai_model():
    return os.getenv("OPENAI_MODEL", "")

# 兼容旧代码
AI_VENDOR = get_ai_vendor()
GEMINI_API_KEY = get_gemini_api_key()
DIFY_API_KEY = get_dify_api_key()
DIFY_DATASET_ID = get_dify_dataset_id()
LLM_MODEL = get_llm_model()
OPENROUTER_API_KEY = get_openrouter_api_key()
OPENAI_MODEL = get_openai_model()
